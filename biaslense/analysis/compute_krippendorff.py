"""
Compute Krippendorff's alpha (inter-rater agreement) for each dimension and model.
Uses ordinal metric appropriate for 1-5 Likert scale ratings.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path


def krippendorff_alpha_ordinal(data):
    """
    Compute Krippendorff's alpha for ordinal data (1-5 scale).

    Args:
        data: 2D array or DataFrame, shape (n_raters, n_items)
              Each row = one rater, each column = one item
              Missing values = NaN

    Returns:
        alpha: float, Krippendorff's alpha value
    """
    data = np.asarray(data)
    n_raters, n_items = data.shape

    # Remove columns (items) with no data
    valid_cols = ~np.all(np.isnan(data), axis=0)
    data = data[:, valid_cols]
    n_items = data.shape[1]

    if n_items == 0:
        return np.nan

    # Pairable values (not NaN)
    m_k = np.nansum(~np.isnan(data), axis=0)  # count of raters per item
    n_pairs = np.sum(m_k * (m_k - 1) / 2)  # total pairable pairs

    if n_pairs == 0:
        return np.nan

    # Coincidence matrix (for ordinal, use distance-weighted)
    # For ordinal data, distance = (value_i - value_j)^2
    values = np.nanmean(data, axis=0)  # rough estimate of scale
    min_val = np.nanmin(data)
    max_val = np.nanmax(data)

    coincidence = np.zeros((int(max_val) + 1, int(max_val) + 1))

    # Build coincidence matrix
    for item_idx in range(n_items):
        col = data[:, item_idx]
        valid = col[~np.isnan(col)]

        for i, val_i in enumerate(valid):
            for j, val_j in enumerate(valid):
                if i != j:
                    coincidence[int(val_i), int(val_j)] += 1 / (len(valid) - 1)

    # Marginal totals
    n_total = np.sum(coincidence)
    marginals = np.sum(coincidence, axis=1)

    # Expected disagreement (under independence assumption)
    d_e = 0.0
    for k in range(len(coincidence)):
        for l in range(len(coincidence)):
            if n_total > 0:
                d_e += (marginals[k] / n_total) * (marginals[l] / (n_total - 1)) * (k - l) ** 2

    # Observed disagreement
    d_o = 0.0
    for k in range(len(coincidence)):
        for l in range(len(coincidence)):
            if n_total > 0:
                d_o += (coincidence[k, l] / n_total) * (k - l) ** 2

    # Alpha
    if d_e == 0:
        return 1.0 if d_o == 0 else 0.0

    alpha = 1.0 - (d_o / d_e)
    return alpha


def load_data():
    """Load combined rater data."""
    # Use environment variable or default relative path for portability
    output_dir = os.environ.get(
        "BIASLENSE_OUTPUT_DIR",
        os.path.join(os.path.dirname(__file__), "../../results")
    )
    data_path = Path(output_dir) / "rater_data_combined.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}\nSet BIASLENSE_OUTPUT_DIR to override data directory")

    return pd.read_csv(data_path)


def compute_alpha_by_model_dimension(df):
    """Compute Krippendorff's alpha for each model and dimension."""

    rating_cols = ['accuracy', 'relevance', 'fairness', 'neutrality', 'representation']
    models = df['model'].unique()

    results = []

    for model in sorted(models):
        model_data = df[df['model'] == model]

        for dimension in rating_cols:
            if dimension not in model_data.columns:
                continue

            # Pivot: rows = raters, columns = prompts
            rater_scores = model_data.pivot_table(
                index='rater',
                columns='prompt_id',
                values=dimension,
                aggfunc='first'
            )

            # Convert to numpy, handle NaNs
            data_matrix = rater_scores.values

            # Compute alpha
            alpha = krippendorff_alpha_ordinal(data_matrix)

            # Interpretation
            if np.isnan(alpha):
                interpretation = "insufficient data"
            elif alpha > 0.61:
                interpretation = "substantial"
            elif alpha > 0.41:
                interpretation = "moderate"
            elif alpha > 0.21:
                interpretation = "fair"
            else:
                interpretation = "poor"

            n_raters = len(rater_scores)
            n_items = len(rater_scores.columns)

            results.append({
                'model': model,
                'dimension': dimension,
                'alpha': round(alpha, 3),
                'interpretation': interpretation,
                'n_raters': n_raters,
                'n_items': n_items,
                'n_pairs': int(np.sum(np.ones(n_raters) * (n_raters - 1) / 2 * n_items))
            })

            print(f"{model} × {dimension:15} α = {alpha:7.3f} ({interpretation:12}) n_raters={n_raters}, n_items={n_items}")

    return pd.DataFrame(results)


def main():
    """Compute and save Krippendorff's alpha results."""

    print("Loading rater data...")
    df = load_data()

    print("\nComputing Krippendorff's alpha (ordinal metric)...")
    print("=" * 100)

    results_df = compute_alpha_by_model_dimension(df)

    # Save results
    output_dir = os.environ.get(
        "BIASLENSE_OUTPUT_DIR",
        os.path.join(os.path.dirname(__file__), "../../results")
    )
    output_path = Path(output_dir) / "krippendorff_alpha_results.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)

    print("\n" + "=" * 100)
    print(f"✓ Saved Krippendorff's alpha results to {output_path}")

    # Summary
    print(f"\n{'='*100}")
    print("SUMMARY BY MODEL")
    print(f"{'='*100}")

    for model in sorted(results_df['model'].unique()):
        model_results = results_df[results_df['model'] == model]
        avg_alpha = model_results['alpha'].mean()
        print(f"\n{model}:")
        print(f"  Average α across dimensions: {avg_alpha:.3f}")

        for _, row in model_results.iterrows():
            print(f"    {row['dimension']:15} α = {row['alpha']:7.3f} ({row['interpretation']:12})")

    return results_df


if __name__ == "__main__":
    results = main()
