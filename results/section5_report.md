# Section 5 results — prompt-level mitigation, recomputed

Generated 2026-11-20 by `biaslense/analysis/paper_section5.py`.

## Data
- Mitigated responses: `biaslense/data/mitigation_ratings.csv` — 5 prompts x 3 models x 3 strategies = 45 ratings,
  one rating each (transcribed from the Drive sheet "Sikh Bias in LLMs - Improved Responses").
- Baseline: the same 5 prompts in `results/rater_data_combined.csv`, averaged over each model's raters
  (2 raters for GPT-4 and LLaMA, 1 for Claude).
- Bias Score = mean(Fairness, Neutrality, Representation).

## Bias Score by model and condition
| model | baseline | instructional | contextual | retrieval | delta_instructional | delta_contextual | delta_retrieval |
|---|---|---|---|---|---|---|---|
| GPT-4 | 2.93 | 4.33 | 3.93 | 4.53 | 1.4 | 1.0 | 1.6 |
| Claude-3 Haiku | 3.0 | 3.33 | 3.53 | 3.6 | 0.33 | 0.53 | 0.6 |
| LLaMA 3.3-70B | 2.03 | 3.53 | 3.53 | 3.87 | 1.5 | 1.5 | 1.83 |

## Per-dimension change, pooled over models
| strategy | measure | baseline | mitigated | change | pct_change |
|---|---|---|---|---|---|
| instructional | accuracy | 3.63 | 3.87 | 0.23 | 6.4 |
| instructional | relevance | 3.87 | 3.8 | -0.07 | -1.7 |
| instructional | fairness | 2.5 | 3.8 | 1.3 | 52.0 |
| instructional | neutrality | 2.7 | 3.8 | 1.1 | 40.7 |
| instructional | representation | 2.75 | 3.6 | 0.85 | 30.9 |
| instructional | bias_score | 2.66 | 3.73 | 1.08 | 40.6 |
| contextual | accuracy | 3.63 | 4.07 | 0.43 | 11.9 |
| contextual | relevance | 3.87 | 3.73 | -0.13 | -3.4 |
| contextual | fairness | 2.5 | 3.53 | 1.03 | 41.3 |
| contextual | neutrality | 2.7 | 4.13 | 1.43 | 53.1 |
| contextual | representation | 2.75 | 3.33 | 0.58 | 21.2 |
| contextual | bias_score | 2.66 | 3.67 | 1.01 | 38.1 |
| retrieval | accuracy | 3.63 | 4.4 | 0.77 | 21.1 |
| retrieval | relevance | 3.87 | 4.27 | 0.4 | 10.3 |
| retrieval | fairness | 2.5 | 4.07 | 1.57 | 62.7 |
| retrieval | neutrality | 2.7 | 3.93 | 1.23 | 45.7 |
| retrieval | representation | 2.75 | 4.0 | 1.25 | 45.5 |
| retrieval | bias_score | 2.66 | 4.0 | 1.34 | 50.6 |

## Tests (Wilcoxon signed-rank vs baseline, 15 model-prompt pairs, Bonferroni x3)
| strategy | n_pairs | mean_change | statistic | p_value | p_adjusted | significant |
|---|---|---|---|---|---|---|
| instructional | 15 | 1.08 | 15.0 | 0.0185 | 0.0555 | False |
| contextual | 15 | 1.01 | 9.5 | 0.0118 | 0.0355 | True |
| retrieval | 15 | 1.34 | 0.0 | 0.0014 | 0.0043 | True |

## Interpretation
- Strategies with a significant Bias Score change after correction: contextual, retrieval.
- Per-model comparisons use 5 prompts each and cannot reach significance on their own; read them as descriptive.

## Limitations (must accompany any claim from this section)
1. Selection and regression to the mean: the 5 prompts were chosen because they scored low at baseline,
   so re-rated scores would tend to rise even with no intervention. Gains here are an upper bound.
2. Rater confound: baseline scores come from the study raters; mitigated responses were rated separately
   (one rating each), so rater differences are mixed into the change.
3. Many mitigated ratings give the same score on all five dimensions, which suggests holistic rather
   than per-dimension judgment.
4. Retrieval prompts are longer and supply facts, which may raise Accuracy and Relevance on their own.
