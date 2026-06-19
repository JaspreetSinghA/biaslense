"""
Scorer validation pipeline — Tasks 1–5 from the scorer rebuild spec.

Usage:
    python tasks/validate_scorer.py [--dev-only] [--inspect] [--test]

Flags:
    --dev-only   Score DEV set only (default on first run)
    --inspect    Print full disagreement analysis (≥2-point gaps)
    --test       Score TEST set (run once, when prompt is final)

Split is deterministic: seed=42, 8 TEST rows, 30 DEV rows.
TEST IDs are recorded but TEST set is only scored when --test is passed.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import numpy as np

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from biaslense.src.core.llm_scorer import LLMScorer

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
DATA_FILE = REPO_ROOT / "data" / "llm_sikh_bias_responses_Jaspreet_claude-3-haiku-20240307.csv"
SPLIT_FILE = REPO_ROOT / "data" / "scorer_split.json"
DEV_RESULTS_FILE = REPO_ROOT / "data" / "dev_scores.csv"
TEST_RESULTS_FILE = REPO_ROOT / "data" / "test_scores.csv"

DIMS = ["Accuracy", "Relevance", "Fairness", "Neutrality", "Representation"]
DIMS_LOWER = [d.lower() for d in DIMS]

RANDOM_SEED = 42
N_TEST = 8

# These rows are embedded as few-shot calibration examples in the scorer prompt.
# They are excluded from DEV scoring to avoid evaluating the scorer on its own training signal.
FEW_SHOT_IDS = {"LING_MODIFIER_01", "REP_IDENTITY_02", "KNOW_HISTORICAL_02", "KNOW_HISTORICAL_04"}


# ── Task 1: Split ──────────────────────────────────────────────────────────────

def make_or_load_split(df: pd.DataFrame) -> dict:
    """
    If SPLIT_FILE exists, load and return it.
    Otherwise create an 8/30 split, save it, and return it.
    """
    if SPLIT_FILE.exists():
        with open(SPLIT_FILE) as f:
            split = json.load(f)
        print(f"[split] Loaded existing split from {SPLIT_FILE.name}")
        return split

    rng = np.random.default_rng(seed=RANDOM_SEED)
    all_ids = df["Prompt ID"].tolist()
    test_ids = rng.choice(all_ids, size=N_TEST, replace=False).tolist()
    dev_ids = [pid for pid in all_ids if pid not in test_ids]

    split = {"test": sorted(test_ids), "dev": sorted(dev_ids)}
    SPLIT_FILE.parent.mkdir(exist_ok=True)
    with open(SPLIT_FILE, "w") as f:
        json.dump(split, f, indent=2)

    print(f"[split] Created new split → {len(dev_ids)} DEV, {len(test_ids)} TEST")
    print(f"[split] TEST IDs (hold-out — do not tune on these): {test_ids}")
    return split


# ── Task 2: Scoring ────────────────────────────────────────────────────────────

def score_rows(scorer: LLMScorer, rows: pd.DataFrame, label: str, out_file: Path) -> pd.DataFrame:
    """
    Score each row with the LLM scorer. Append results to out_file so
    the run can be resumed if interrupted (skips already-scored rows).
    Returns a DataFrame with human scores + model scores merged.
    """
    # Load any partial results
    already_done: set = set()
    if out_file.exists():
        done = pd.read_csv(out_file)
        already_done = set(done["Prompt ID"].tolist())
        print(f"[{label}] Resuming — {len(already_done)} rows already scored")

    results = []
    todo = rows[~rows["Prompt ID"].isin(already_done)]
    print(f"[{label}] Scoring {len(todo)} rows…")

    for i, (_, row) in enumerate(todo.iterrows()):
        pid = row["Prompt ID"]
        try:
            result = scorer.score(
                response_text=str(row["Response"]),
                prompt_text=str(row["Prompt Text"]),
            )
            record = {
                "Prompt ID": pid,
                "Category": row["Category"],
                "h_Accuracy": row["Accuracy"],
                "h_Relevance": row["Relevance"],
                "h_Fairness": row["Fairness"],
                "h_Neutrality": row["Neutrality"],
                "h_Representation": row["Representation"],
                "m_Accuracy": result.accuracy,
                "m_Relevance": result.relevance,
                "m_Fairness": result.fairness,
                "m_Neutrality": result.neutrality,
                "m_Representation": result.representation,
                "r_Accuracy": result.accuracy_reason,
                "r_Relevance": result.relevance_reason,
                "r_Fairness": result.fairness_reason,
                "r_Neutrality": result.neutrality_reason,
                "r_Representation": result.representation_reason,
            }
            results.append(record)
            print(f"  [{i+1}/{len(todo)}] {pid} ✓")
        except Exception as e:
            print(f"  [{i+1}/{len(todo)}] {pid} ERROR: {e}")
            continue

        # Append after each row so we can resume on crash
        new_df = pd.DataFrame(results)
        if out_file.exists():
            existing = pd.read_csv(out_file)
            combined = pd.concat([existing, new_df], ignore_index=True)
        else:
            combined = new_df
        combined.to_csv(out_file, index=False)
        results = []  # Reset buffer (already saved)

        # Polite rate-limiting: 0.5 s between calls
        time.sleep(0.5)

    # Return full merged result
    full = pd.read_csv(out_file)
    return full


# ── Task 3: Agreement metrics ─────────────────────────────────────────────────

def compute_agreement(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each dimension, compute:
      - exact match rate
      - within-1-point rate
      - mean absolute error
    Returns a 5-row DataFrame.
    """
    rows = []
    for dim in DIMS:
        h = df[f"h_{dim}"].astype(float)
        m = df[f"m_{dim}"].astype(float)
        diff = (h - m).abs()
        rows.append({
            "Dimension": dim,
            "Exact%": round(100 * (diff == 0).mean(), 1),
            "Within1%": round(100 * (diff <= 1).mean(), 1),
            "MAE": round(diff.mean(), 3),
            "N": len(df),
        })
    return pd.DataFrame(rows)


# ── Task 4: Disagreement inspection ───────────────────────────────────────────

def inspect_disagreements(df: pd.DataFrame, threshold: int = 2):
    """Print rows where |human - model| >= threshold on any dimension."""
    print(f"\n{'='*70}")
    print(f"DISAGREEMENTS (|human - model| ≥ {threshold} on any dimension)")
    print(f"{'='*70}")

    found = 0
    for _, row in df.iterrows():
        for dim in DIMS:
            h = float(row[f"h_{dim}"])
            m = float(row[f"m_{dim}"])
            gap = abs(h - m)
            if gap >= threshold:
                found += 1
                print(f"\nPrompt ID : {row['Prompt ID']}")
                print(f"Category  : {row['Category']}")
                print(f"Dimension : {dim}")
                print(f"Human     : {int(h)}   Model : {int(m)}   Gap : {int(gap)}")
                reason_col = f"r_{dim}"
                print(f"Reason    : {row.get(reason_col, '(no reason)')}")
                print(f"Action    : [classify manually — (a) prompt ambiguity, (b) model error, or (c) label questionable]")

    if found == 0:
        print("No disagreements found at this threshold.")
    else:
        print(f"\nTotal disagreements: {found}")


# ── Main ───────────────────────────────────────────────────────────────────────

def print_table(title: str, agreement: pd.DataFrame):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    header = f"{'Dimension':<18} {'Exact%':>8} {'Within1%':>10} {'MAE':>8} {'N':>5}"
    print(header)
    print("-" * 55)
    for _, r in agreement.iterrows():
        print(f"{r['Dimension']:<18} {r['Exact%']:>7.1f}% {r['Within1%']:>9.1f}% {r['MAE']:>8.3f} {r['N']:>5}")
    print("-" * 55)
    avg_exact = agreement["Exact%"].mean()
    avg_w1 = agreement["Within1%"].mean()
    avg_mae = agreement["MAE"].mean()
    print(f"{'AVERAGE':<18} {avg_exact:>7.1f}% {avg_w1:>9.1f}% {avg_mae:>8.3f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-only", action="store_true", default=False)
    parser.add_argument("--inspect", action="store_true", default=False)
    parser.add_argument("--test", action="store_true", default=False)
    args = parser.parse_args()

    # Load data
    df = pd.read_csv(DATA_FILE)
    print(f"[data] Loaded {len(df)} rows from {DATA_FILE.name}")

    # Task 1: Split
    split = make_or_load_split(df)
    dev_df = df[df["Prompt ID"].isin(split["dev"])].reset_index(drop=True)
    test_df = df[df["Prompt ID"].isin(split["test"])].reset_index(drop=True)
    print(f"[split] DEV={len(dev_df)}  TEST={len(test_df)}")

    # Init scorer
    scorer = LLMScorer()

    # Task 3: DEV scoring and agreement (exclude few-shot rows — they're in the prompt)
    dev_scoreable = dev_df[~dev_df["Prompt ID"].isin(FEW_SHOT_IDS)].reset_index(drop=True)
    n_excluded = len(dev_df) - len(dev_scoreable)
    print(f"\n[DEV] Scoring DEV set (excluding {n_excluded} few-shot rows: {sorted(FEW_SHOT_IDS)})…")
    dev_results = score_rows(scorer, dev_scoreable, "DEV", DEV_RESULTS_FILE)
    dev_agreement = compute_agreement(dev_results)
    print_table(f"DEV SET — Agreement (N={len(dev_results)}, excl. few-shot rows)", dev_agreement)

    if args.inspect:
        inspect_disagreements(dev_results)

    # Task 5: TEST scoring (only when --test flag is passed)
    if args.test:
        print("\n[TEST] Scoring TEST set…")
        test_results = score_rows(scorer, test_df, "TEST", TEST_RESULTS_FILE)
        test_agreement = compute_agreement(test_results)
        print_table("TEST SET — Agreement (N=8)  ← honest numbers", test_agreement)

        if args.inspect:
            inspect_disagreements(test_results)

    # Task 6: Embedding checker recommendation (always printed)
    print(f"""
{'='*60}
TASK 6 — Embedding Checker Recommendation
{'='*60}
The LLM scorer (this script) reads meaning, not keywords.
It handles all cases the embedding checker was designed for:
stereotype detection, nuanced framing, semantic similarity to bias.

The embedding_checker.py also has a confirmed bug at line 125:
  `if not self.stereotype_embeddings is not None:`
which is a double-negative — always False — so embeddings never run.

Recommendation: DELETE embedding_checker.py.
Rationale: (1) The LLM scorer supersedes its use case.
           (2) The bug means it was never functioning anyway.
           (3) Removing dead code simplifies the codebase.
If TEST agreement is satisfactory (within-1 > 70% on all dims),
the LLM scorer is the sole scorer — no need for embedding backup.
""")


if __name__ == "__main__":
    main()
