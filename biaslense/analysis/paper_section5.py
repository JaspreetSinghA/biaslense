"""
Recompute the paper's Section 5 (prompt-level mitigation) from source data.

Inputs
    biaslense/data/mitigation_ratings.csv   45 ratings: 3 strategies x 3 models x 5 prompts
                                            (transcribed from the Drive sheet
                                            "Sikh Bias in LLMs - Improved Responses")
    results/rater_data_combined.csv         baseline ratings for the same prompts

Outputs
    results/section5_summary.csv      Bias Score per model x condition (baseline + 3 strategies)
    results/section5_dimensions.csv   per-dimension means and % change vs baseline, pooled over models
    results/section5_tests.csv        Wilcoxon signed-rank per strategy vs baseline (15 pairs)
    results/section5_report.md        methodology, tables, interpretation, limitations
    docs/paper/figures/fig4_mitigation.png

Bias Score = mean of Fairness, Neutrality, Representation (the paper's definition).
Baseline per (model, prompt) = mean of that model's raters for the prompt.

Run:  python -m biaslense.analysis.paper_section5
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from biaslense.analysis.paper_section3 import (  # noqa: E402
    FIGURE_DPI, FIGURES_DIR, GRID, MODEL_COLORS, MODEL_LABELS, MODELS, RESULTS_DIR, SURFACE,
    TEXT_PRIMARY, TEXT_SECONDARY, _bonferroni, _style_axes, _to_markdown,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MITIGATION_CSV = REPO_ROOT / "biaslense" / "data" / "mitigation_ratings.csv"
RATINGS_CSV = RESULTS_DIR / "rater_data_combined.csv"

DIMENSIONS = ["accuracy", "relevance", "fairness", "neutrality", "representation"]
BIAS_DIMENSIONS = ["fairness", "neutrality", "representation"]
BIAS_SCORE = "bias_score"
BASELINE = "baseline"
STRATEGIES = ["instructional", "contextual", "retrieval"]
CONDITIONS = [BASELINE, *STRATEGIES]
CONDITION_LABELS = {BASELINE: "Baseline", "instructional": "Instructional",
                    "contextual": "Contextual reframing", "retrieval": "Retrieval grounding"}
ALPHA_LEVEL = 0.05


def load_conditions() -> pd.DataFrame:
    """One row per (condition, model, prompt) with all dimensions and the Bias Score."""
    mitigated = pd.read_csv(MITIGATION_CSV).rename(columns={"strategy": "condition"})
    prompts = mitigated["prompt_id"].unique()
    baseline_ratings = pd.read_csv(RATINGS_CSV)
    baseline = (
        baseline_ratings[baseline_ratings["prompt_id"].isin(prompts)]
        .groupby(["model", "prompt_id"], as_index=False)[DIMENSIONS].mean()
        .assign(condition=BASELINE)
    )
    combined = pd.concat([baseline, mitigated], ignore_index=True)
    combined[BIAS_SCORE] = combined[BIAS_DIMENSIONS].mean(axis=1)
    expected = len(CONDITIONS) * len(MODELS) * len(prompts)
    if len(combined) != expected:
        raise ValueError(f"expected {expected} condition rows, found {len(combined)}")
    return combined


def summarize(conditions: pd.DataFrame) -> pd.DataFrame:
    """Mean Bias Score per model x condition, plus each strategy's change from baseline."""
    table = conditions.pivot_table(index="model", columns="condition", values=BIAS_SCORE).loc[MODELS, CONDITIONS]
    for strategy in STRATEGIES:
        table[f"delta_{strategy}"] = table[strategy] - table[BASELINE]
    table.index = [MODEL_LABELS[m] for m in table.index]
    return table.round(2)


def dimension_changes(conditions: pd.DataFrame) -> pd.DataFrame:
    """Per-dimension mean by condition (pooled over models) and % change vs baseline."""
    means = conditions.groupby("condition")[DIMENSIONS + [BIAS_SCORE]].mean().loc[CONDITIONS]
    rows = []
    for strategy in STRATEGIES:
        for col in DIMENSIONS + [BIAS_SCORE]:
            base, new = means.loc[BASELINE, col], means.loc[strategy, col]
            rows.append({"strategy": strategy, "measure": col, "baseline": round(base, 2), "mitigated": round(new, 2),
                         "change": round(new - base, 2), "pct_change": round(100 * (new - base) / base, 1)})
    return pd.DataFrame(rows)


def run_tests(conditions: pd.DataFrame) -> pd.DataFrame:
    """Wilcoxon signed-rank on Bias Score, each strategy vs baseline, over the 15
    (model, prompt) pairs; Bonferroni across the three strategies."""
    wide = conditions.pivot_table(index=["model", "prompt_id"], columns="condition", values=BIAS_SCORE)
    rows = []
    for strategy in STRATEGIES:
        stat, p = stats.wilcoxon(wide[strategy], wide[BASELINE])
        p_adj = _bonferroni(p, len(STRATEGIES))
        rows.append({"strategy": strategy, "n_pairs": len(wide),
                     "mean_change": round((wide[strategy] - wide[BASELINE]).mean(), 2),
                     "statistic": round(stat, 3), "p_value": round(p, 4), "p_adjusted": round(p_adj, 4),
                     "significant": p_adj < ALPHA_LEVEL})
    return pd.DataFrame(rows)


def plot_mitigation(summary: pd.DataFrame, path: Path) -> None:
    """Figure 4: mean Bias Score per condition, one column per model (colors match Figs 1-2)."""
    fig, ax = plt.subplots(figsize=(8, 3.8), facecolor=SURFACE)
    _style_axes(ax)
    bar_width, gap = 0.24, 0.02
    offsets = np.array([-1, 0, 1]) * (bar_width + gap)
    x = np.arange(len(CONDITIONS))
    for offset, model in zip(offsets, MODELS):
        values = summary.loc[MODEL_LABELS[model], CONDITIONS].to_numpy(dtype=float)
        ax.bar(x + offset, values, width=bar_width, color=MODEL_COLORS[model], label=MODEL_LABELS[model])
    ax.set_xticks(x, [CONDITION_LABELS[c] for c in CONDITIONS], color=TEXT_PRIMARY, fontsize=9)
    ax.set_ylim(1, 5)
    ax.set_yticks(range(1, 6))
    ax.set_ylabel("Mean Bias Score (1-5)", color=TEXT_SECONDARY, fontsize=9)
    ax.spines["bottom"].set_color(GRID)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False,
              fontsize=9, labelcolor=TEXT_PRIMARY)
    fig.tight_layout()
    fig.savefig(path, dpi=FIGURE_DPI, facecolor=SURFACE)
    plt.close(fig)


def write_report(summary: pd.DataFrame, dims: pd.DataFrame, tests: pd.DataFrame, path: Path) -> None:
    """Write a self-contained Markdown report with the caveats the design requires."""
    sig = tests[tests["significant"]]["strategy"].tolist()
    report = f"""# Section 5 results — prompt-level mitigation, recomputed

Generated {dt.date.today().isoformat()} by `biaslense/analysis/paper_section5.py`.

## Data
- Mitigated responses: `biaslense/data/mitigation_ratings.csv` — 5 prompts x 3 models x 3 strategies = 45 ratings,
  one rating each (transcribed from the Drive sheet "Sikh Bias in LLMs - Improved Responses").
- Baseline: the same 5 prompts in `results/rater_data_combined.csv`, averaged over each model's raters
  (2 raters for GPT-4 and LLaMA, 1 for Claude).
- Bias Score = mean(Fairness, Neutrality, Representation).

## Bias Score by model and condition
{_to_markdown(summary.reset_index().rename(columns={'index': 'model'}))}

## Per-dimension change, pooled over models
{_to_markdown(dims)}

## Tests (Wilcoxon signed-rank vs baseline, 15 model-prompt pairs, Bonferroni x3)
{_to_markdown(tests)}

## Interpretation
- Strategies with a significant Bias Score change after correction: {', '.join(sig) if sig else 'none'}.
- Per-model comparisons use 5 prompts each and cannot reach significance on their own; read them as descriptive.

## Limitations (must accompany any claim from this section)
1. Selection and regression to the mean: the 5 prompts were chosen because they scored low at baseline,
   so re-rated scores would tend to rise even with no intervention. Gains here are an upper bound.
2. Rater confound: baseline scores come from the study raters; mitigated responses were rated separately
   (one rating each), so rater differences are mixed into the change.
3. Many mitigated ratings give the same score on all five dimensions, which suggests holistic rather
   than per-dimension judgment.
4. Retrieval prompts are longer and supply facts, which may raise Accuracy and Relevance on their own.
"""
    path.write_text(report)


def main() -> None:
    """Compute Section 5 tables, tests, figure, and report."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    conditions = load_conditions()
    summary = summarize(conditions)
    dims = dimension_changes(conditions)
    tests = run_tests(conditions)

    summary.to_csv(RESULTS_DIR / "section5_summary.csv")
    dims.to_csv(RESULTS_DIR / "section5_dimensions.csv", index=False)
    tests.to_csv(RESULTS_DIR / "section5_tests.csv", index=False)
    plot_mitigation(summary, FIGURES_DIR / "fig4_mitigation.png")
    write_report(summary, dims, tests, RESULTS_DIR / "section5_report.md")
    print(f"Wrote Section 5 outputs to {RESULTS_DIR} and {FIGURES_DIR}")


if __name__ == "__main__":
    main()
