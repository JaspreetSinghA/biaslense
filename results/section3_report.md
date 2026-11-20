# Section 3 results — rebuilt from the 276-rating dataset

Generated 2026-11-20 by `biaslense/analysis/paper_section3.py`.

## Data
- Ratings: `results/rater_data_combined.csv` (276 ratings, 6 raters, 3 models, 54 prompts; 1-5 scale, higher = less biased).
- Prompt categories: `biaslense/data/*.xlsx` ("Category" column).
- Composite = mean of the five dimensions for a rating.

## Method
- Table 1 summarizes every rating.
- Tests and category means use one score per (model, prompt): the mean of that model's raters.
- Model differences: Friedman test (non-parametric, repeated measures) on the prompts all three models share
  (n = 44; Claude-3 Haiku was rated on 44 of 54 prompts). Chosen over ANOVA because ratings are ordinal and
  the same prompts are answered by every model.
- Category differences: Kruskal-Wallis test on composite scores across the five bias categories.
- Significance level: 0.05, Bonferroni-adjusted (x6 across Friedman measures; x3 across pairwise Wilcoxon follow-ups).

## Table 1 — mean ± SD by model and dimension
| Model | n ratings | n prompts | Accuracy | Relevance | Fairness | Neutrality | Representation | Composite |
|---|---|---|---|---|---|---|---|---|
| GPT-4 | 108 | 54 | 4.10 ± 0.98 | 4.21 ± 1.05 | 3.44 ± 1.26 | 3.54 ± 1.40 | 3.62 ± 1.42 | 3.78 ± 0.82 |
| Claude-3 Haiku | 60 | 44 | 3.52 ± 1.08 | 4.00 ± 0.97 | 3.40 ± 1.18 | 3.62 ± 1.18 | 4.03 ± 1.07 | 3.71 ± 0.71 |
| LLaMA 3.3-70B | 108 | 54 | 3.77 ± 0.97 | 3.93 ± 0.92 | 3.54 ± 1.15 | 3.56 ± 1.19 | 3.59 ± 1.25 | 3.68 ± 0.91 |

## Category means (composite, per-prompt averages)
| category | GPT-4 | Claude-3 Haiku | LLaMA 3.3-70B | n GPT-4 | n Claude-3 Haiku | n LLaMA 3.3-70B |
|---|---|---|---|---|---|---|
| Comparative Equity Assessment | 3.72 | 3.74 | 4.04 | 14 | 11 | 14 |
| Knowledge-Based Bias | 4.08 | 4.1 | 3.69 | 10 | 9 | 10 |
| Linguistic Bias | 3.54 | 3.49 | 3.21 | 10 | 8 | 10 |
| Representational Bias | 3.67 | 3.46 | 3.34 | 10 | 9 | 10 |
| Structural Bias | 3.93 | 3.4 | 3.95 | 10 | 7 | 10 |

## Tests
| test | measure | n | statistic | p_value | p_adjusted | significant |
|---|---|---|---|---|---|---|
| Friedman (model) | accuracy | 44 | 14.959 | 0.0006 | 0.0034 | True |
| Wilcoxon GPT-4 vs Claude-3 Haiku (mean diff +0.66) | accuracy | 44 | 139.5 | 0.0007 | 0.0022 | True |
| Wilcoxon GPT-4 vs LLaMA 3.3-70B (mean diff +0.47) | accuracy | 44 | 97.5 | 0.0016 | 0.0047 | True |
| Wilcoxon Claude-3 Haiku vs LLaMA 3.3-70B (mean diff -0.19) | accuracy | 44 | 235.0 | 0.2818 | 0.8453 | False |
| Friedman (model) | relevance | 44 | 3.231 | 0.1988 | 1.0 | False |
| Friedman (model) | fairness | 44 | 0.616 | 0.7348 | 1.0 | False |
| Friedman (model) | neutrality | 44 | 0.245 | 0.8846 | 1.0 | False |
| Friedman (model) | representation | 43 | 6.288 | 0.0431 | 0.2587 | False |
| Friedman (model) | composite | 44 | 2.714 | 0.2574 | 1.0 | False |
| Kruskal-Wallis (category) | composite | 152 | 13.205 | 0.0103 | 0.0103 | True |

## Interpretation
- Model differences significant after Bonferroni: accuracy.
- Bias category effect on composite: H = 13.205, p = 0.0103
  (significant).
- With low inter-rater agreement (Table 2) and 44-54 prompts per model, small mean differences
  between models should not be read as rankings unless the test above supports them.
