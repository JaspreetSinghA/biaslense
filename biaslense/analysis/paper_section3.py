"""
Rebuild the paper's Section 3 (Results) from the 276-rating dataset.

Inputs
    results/rater_data_combined.csv   one row per (rater, model, prompt), 1-5 scores
    biaslense/data/*.xlsx             prompt metadata ("Prompt ID" -> "Category")

Outputs
    results/section3_table1.csv           mean ± SD per model x dimension (+ composite)
    results/section3_category_means.csv   composite mean per bias category x model
    results/section3_tests.csv            Friedman (models) and Kruskal-Wallis (categories)
    results/section3_report.md            methodology, tables, interpretation
    docs/paper/figures/fig1_score_distributions.png
    docs/paper/figures/fig2_category_heatmap.png

Unit of analysis
    Table 1 uses every rating (matches results/dimension_baselines.csv).
    Tests and category means use one score per (model, prompt): the mean of that
    model's raters for the prompt, so each prompt counts once per model.

Run:  python -m biaslense.analysis.paper_section3
"""

from __future__ import annotations

import datetime as dt
import glob
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from scipy import stats  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
RATINGS_CSV = REPO_ROOT / "results" / "rater_data_combined.csv"
PROMPT_METADATA_GLOB = str(REPO_ROOT / "biaslense" / "data" / "*.xlsx")
RESULTS_DIR = REPO_ROOT / "results"
FIGURES_DIR = REPO_ROOT / "docs" / "paper" / "figures"

DIMENSIONS = ["accuracy", "relevance", "fairness", "neutrality", "representation"]
COMPOSITE = "composite"

# Display order and labels; colors are the validated categorical slots 1-3
# (dataviz reference palette, light mode). Color follows the model, never rank.
MODELS = ["gpt-4", "claude-3-haiku", "llama-3.3-70b"]
MODEL_LABELS = {"gpt-4": "GPT-4", "claude-3-haiku": "Claude-3 Haiku", "llama-3.3-70b": "LLaMA 3.3-70B"}
MODEL_COLORS = {"gpt-4": "#2a78d6", "claude-3-haiku": "#eb6834", "llama-3.3-70b": "#1baf7a"}

SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e6e5e1"
# Sequential blue ramp (steps 100 -> 600) for the heatmap.
SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95"]
DARK_CELL_THRESHOLD = 0.55  # normalized value above which cell text switches to white

SCORE_MIN, SCORE_MAX = 1, 5
ALPHA_LEVEL = 0.05
FIGURE_DPI = 300


def load_ratings() -> pd.DataFrame:
    """Load combined ratings, attach each prompt's bias category, and add a composite."""
    ratings = pd.read_csv(RATINGS_CSV)
    categories: dict[str, str] = {}
    for path in glob.glob(PROMPT_METADATA_GLOB):
        meta = pd.read_excel(path)
        categories.update(dict(zip(meta["Prompt ID"], meta["Category"])))
    ratings["category"] = ratings["prompt_id"].map(categories)
    unmapped = ratings["category"].isna().sum()
    if unmapped:
        raise ValueError(f"{unmapped} ratings have no category; check prompt IDs")
    ratings[COMPOSITE] = ratings[DIMENSIONS].mean(axis=1)
    return ratings


def per_prompt_scores(ratings: pd.DataFrame) -> pd.DataFrame:
    """Average raters within each (model, prompt) so every prompt counts once per model."""
    return (
        ratings.groupby(["model", "prompt_id", "category"], as_index=False)[DIMENSIONS + [COMPOSITE]]
        .mean()
    )


def build_table1(ratings: pd.DataFrame) -> pd.DataFrame:
    """Mean ± SD per model and dimension over all ratings, plus rating and prompt counts."""
    rows = []
    for model in MODELS:
        subset = ratings[ratings["model"] == model]
        row = {"model": MODEL_LABELS[model], "n_ratings": len(subset), "n_prompts": subset["prompt_id"].nunique()}
        for col in DIMENSIONS + [COMPOSITE]:
            row[f"{col}_mean"] = round(subset[col].mean(), 2)
            row[f"{col}_sd"] = round(subset[col].std(), 2)
        rows.append(row)
    return pd.DataFrame(rows)


def _bonferroni(p_value: float, n_tests: int) -> float:
    """Bonferroni-adjusted p-value, capped at 1."""
    return min(1.0, p_value * n_tests)


def run_tests(prompt_scores: pd.DataFrame) -> pd.DataFrame:
    """Friedman test across models on prompts all three models share (Bonferroni over the
    six measures); pairwise Wilcoxon signed-rank follow-ups for measures that stay
    significant (Bonferroni over the three pairs); Kruskal-Wallis across bias categories."""
    rows = []
    measures = DIMENSIONS + [COMPOSITE]
    pairs = [(a, b) for i, a in enumerate(MODELS) for b in MODELS[i + 1:]]
    shared = prompt_scores.pivot_table(index="prompt_id", columns="model", values=measures)
    for col in measures:
        complete = shared[col][MODELS].dropna()
        stat, p = stats.friedmanchisquare(*(complete[m] for m in MODELS))
        p_adj = _bonferroni(p, len(measures))
        rows.append({"test": "Friedman (model)", "measure": col, "n": len(complete), "statistic": round(stat, 3),
                     "p_value": round(p, 4), "p_adjusted": round(p_adj, 4), "significant": p_adj < ALPHA_LEVEL})
        if p_adj >= ALPHA_LEVEL:
            continue
        for a, b in pairs:
            w_stat, w_p = stats.wilcoxon(complete[a], complete[b])
            w_adj = _bonferroni(w_p, len(pairs))
            diff = complete[a].mean() - complete[b].mean()
            rows.append({"test": f"Wilcoxon {MODEL_LABELS[a]} vs {MODEL_LABELS[b]} (mean diff {diff:+.2f})",
                         "measure": col, "n": len(complete), "statistic": round(w_stat, 3),
                         "p_value": round(w_p, 4), "p_adjusted": round(w_adj, 4), "significant": w_adj < ALPHA_LEVEL})
    groups = [g[COMPOSITE].values for _, g in prompt_scores.groupby("category")]
    stat, p = stats.kruskal(*groups)
    rows.append({"test": "Kruskal-Wallis (category)", "measure": COMPOSITE, "n": len(prompt_scores),
                 "statistic": round(stat, 3), "p_value": round(p, 4), "p_adjusted": round(p, 4),
                 "significant": p < ALPHA_LEVEL})
    return pd.DataFrame(rows)


def build_category_means(prompt_scores: pd.DataFrame) -> pd.DataFrame:
    """Composite mean per bias category x model, with the number of prompts per cell."""
    grouped = prompt_scores.groupby(["category", "model"])[COMPOSITE]
    table = grouped.mean().round(2).unstack("model")[MODELS]
    counts = grouped.size().unstack("model")[MODELS]
    table.columns = [MODEL_LABELS[m] for m in MODELS]
    counts.columns = [f"n {MODEL_LABELS[m]}" for m in MODELS]
    return table.join(counts)


def _style_axes(ax: plt.Axes) -> None:
    """Recessive axes: hairline solid grid on y, no top/right spines, secondary-ink ticks."""
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=9)
    ax.yaxis.grid(True, color=GRID, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)


def plot_distributions(ratings: pd.DataFrame, path: Path) -> None:
    """Figure 1: box plots of all ratings per dimension, one box per model."""
    fig, ax = plt.subplots(figsize=(9, 4.2), facecolor=SURFACE)
    _style_axes(ax)
    box_width, gap = 0.22, 0.04
    offsets = np.array([-1, 0, 1]) * (box_width + gap)
    for offset, model in zip(offsets, MODELS):
        data = [ratings.loc[ratings["model"] == model, d].dropna() for d in DIMENSIONS]
        positions = np.arange(len(DIMENSIONS)) + offset
        color = MODEL_COLORS[model]
        ax.boxplot(
            data, positions=positions, widths=box_width, patch_artist=True, showfliers=True,
            boxprops={"facecolor": color, "edgecolor": color, "alpha": 0.85},
            medianprops={"color": TEXT_PRIMARY, "linewidth": 2},
            whiskerprops={"color": color, "linewidth": 1.5},
            capprops={"color": color, "linewidth": 1.5},
            flierprops={"marker": "o", "markersize": 4, "markerfacecolor": color,
                        "markeredgecolor": SURFACE, "alpha": 0.8},
        )
        ax.plot([], [], color=color, linewidth=8, label=MODEL_LABELS[model])
    ax.set_xticks(range(len(DIMENSIONS)), [d.capitalize() for d in DIMENSIONS], color=TEXT_PRIMARY)
    ax.set_ylim(SCORE_MIN - 0.3, SCORE_MAX + 0.3)
    ax.set_yticks(range(SCORE_MIN, SCORE_MAX + 1))
    ax.set_ylabel("Rating (1 = most biased, 5 = least)", color=TEXT_SECONDARY, fontsize=9)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False,
              fontsize=9, labelcolor=TEXT_PRIMARY)
    fig.tight_layout()
    fig.savefig(path, dpi=FIGURE_DPI, facecolor=SURFACE)
    plt.close(fig)


def plot_category_heatmap(category_means: pd.DataFrame, path: Path) -> None:
    """Figure 2: composite mean by bias category x model; each cell labeled with value and n."""
    labels = [MODEL_LABELS[m] for m in MODELS]
    values = category_means[labels].to_numpy()
    counts = category_means[[f"n {label}" for label in labels]].to_numpy()
    vmin, vmax = np.floor(values.min() * 4) / 4, np.ceil(values.max() * 4) / 4
    cmap = LinearSegmentedColormap.from_list("seq_blue", SEQUENTIAL_BLUE)

    fig, ax = plt.subplots(figsize=(6.4, 3.8), facecolor=SURFACE)
    image = ax.imshow(values, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    for (i, j), value in np.ndenumerate(values):
        dark = (value - vmin) / (vmax - vmin) > DARK_CELL_THRESHOLD
        ax.text(j, i, f"{value:.2f}\n(n={counts[i, j]})", ha="center", va="center", fontsize=8.5,
                color=SURFACE if dark else TEXT_PRIMARY)
    ax.set_xticks(range(len(labels)), labels, color=TEXT_PRIMARY, fontsize=9)
    ax.set_yticks(range(len(category_means)), category_means.index, color=TEXT_PRIMARY, fontsize=9)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    # 2px surface gap between interior cells
    for x in np.arange(0.5, len(labels) - 1):
        ax.axvline(x, color=SURFACE, linewidth=2)
    for y in np.arange(0.5, len(category_means) - 1):
        ax.axhline(y, color=SURFACE, linewidth=2)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.04, pad=0.03)
    colorbar.set_label("Mean composite score (1-5)", color=TEXT_SECONDARY, fontsize=8.5)
    colorbar.outline.set_visible(False)
    for spine in colorbar.ax.spines.values():
        spine.set_visible(False)
    colorbar.ax.tick_params(colors=TEXT_SECONDARY, labelsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=FIGURE_DPI, facecolor=SURFACE)
    plt.close(fig)


def _to_markdown(frame: pd.DataFrame) -> str:
    """Render a DataFrame as a Markdown table without the optional 'tabulate' dependency."""
    header = "| " + " | ".join(str(c) for c in frame.columns) + " |"
    divider = "|" + "---|" * len(frame.columns)
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in frame.itertuples(index=False)]
    return "\n".join([header, divider, *body])


def _format_table1(table1: pd.DataFrame) -> str:
    """Render Table 1 as Markdown with 'mean ± SD' cells."""
    cols = DIMENSIONS + [COMPOSITE]
    header = "| Model | n ratings | n prompts | " + " | ".join(c.capitalize() for c in cols) + " |"
    lines = [header, "|" + "---|" * (len(cols) + 3)]
    for _, r in table1.iterrows():
        cells = " | ".join(f"{r[f'{c}_mean']:.2f} ± {r[f'{c}_sd']:.2f}" for c in cols)
        lines.append(f"| {r['model']} | {r['n_ratings']} | {r['n_prompts']} | {cells} |")
    return "\n".join(lines)


def write_report(table1: pd.DataFrame, category_means: pd.DataFrame, tests: pd.DataFrame, path: Path) -> None:
    """Write a self-contained Markdown report: sources, method, tables, interpretation."""
    friedman = tests[tests["test"].str.startswith(("Friedman", "Wilcoxon"))]
    kruskal = tests[tests["test"].str.startswith("Kruskal")].iloc[0]
    significant = friedman[friedman["significant"] & (friedman["test"] == "Friedman (model)")]["measure"].tolist()
    report = f"""# Section 3 results — rebuilt from the 276-rating dataset

Generated {dt.date.today().isoformat()} by `biaslense/analysis/paper_section3.py`.

## Data
- Ratings: `results/rater_data_combined.csv` ({int(table1['n_ratings'].sum())} ratings, 6 raters, 3 models, 54 prompts; 1-5 scale, higher = less biased).
- Prompt categories: `biaslense/data/*.xlsx` ("Category" column).
- Composite = mean of the five dimensions for a rating.

## Method
- Table 1 summarizes every rating.
- Tests and category means use one score per (model, prompt): the mean of that model's raters.
- Model differences: Friedman test (non-parametric, repeated measures) on the prompts all three models share
  (n = {int(friedman['n'].iloc[0])}; Claude-3 Haiku was rated on 44 of 54 prompts). Chosen over ANOVA because ratings are ordinal and
  the same prompts are answered by every model.
- Category differences: Kruskal-Wallis test on composite scores across the five bias categories.
- Significance level: {ALPHA_LEVEL}, Bonferroni-adjusted (x6 across Friedman measures; x3 across pairwise Wilcoxon follow-ups).

## Table 1 — mean ± SD by model and dimension
{_format_table1(table1)}

## Category means (composite, per-prompt averages)
{_to_markdown(category_means.reset_index())}

## Tests
{_to_markdown(tests)}

## Interpretation
- Model differences significant after Bonferroni: {', '.join(significant) if significant else 'none'}.
- Bias category effect on composite: H = {kruskal['statistic']}, p = {kruskal['p_value']}
  ({'significant' if kruskal['significant'] else 'not significant'}).
- With low inter-rater agreement (Table 2) and 44-54 prompts per model, small mean differences
  between models should not be read as rankings unless the test above supports them.
"""
    path.write_text(report)


def main() -> None:
    """Compute Section 3 tables, tests, figures, and report."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    ratings = load_ratings()
    prompt_scores = per_prompt_scores(ratings)

    table1 = build_table1(ratings)
    category_means = build_category_means(prompt_scores)
    tests = run_tests(prompt_scores)

    table1.to_csv(RESULTS_DIR / "section3_table1.csv", index=False)
    category_means.to_csv(RESULTS_DIR / "section3_category_means.csv")
    tests.to_csv(RESULTS_DIR / "section3_tests.csv", index=False)
    plot_distributions(ratings, FIGURES_DIR / "fig1_score_distributions.png")
    plot_category_heatmap(category_means, FIGURES_DIR / "fig2_category_heatmap.png")
    write_report(table1, category_means, tests, RESULTS_DIR / "section3_report.md")
    print(f"Wrote Section 3 outputs to {RESULTS_DIR} and {FIGURES_DIR}")


if __name__ == "__main__":
    main()
