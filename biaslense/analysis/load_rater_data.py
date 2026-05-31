"""
Load and merge rater evaluation data from all CSV files.
Produces a combined dataset and summary statistics.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path


# Use environment variables or defaults for portability
RATER_DATA_DIR = os.environ.get(
    "RATER_DATA_DIR",
    os.path.expanduser("~/projects/data/processed/")
)

# Output directory relative to package or from environment
OUTPUT_DIR = Path(
    os.environ.get(
        "BIASLENSE_OUTPUT_DIR",
        os.path.join(os.path.dirname(__file__), "../../results")
    )
).resolve()
OUTPUT_DIR.mkdir(exist_ok=True)

# Rater files mapping: (filename, rater_name, model_name)
RATER_FILES = [
    ("llm_sikh_bias_responses_Gurleen_gpt-4.csv", "Gurleen", "gpt-4"),
    ("llm_sikh_bias_responses_Noor_gpt-4.csv", "Noor", "gpt-4"),
    ("llm_sikh_bias_responses_Anu_llama-3.3-70b-versatile.csv", "Anu", "llama-3.3-70b"),
    ("llm_sikh_bias_responses_Harpreet_llama-3.3-70b-versatile.csv", "Harpreet", "llama-3.3-70b"),
    ("llm_sikh_bias_responses_Jaspreet_claude-3-haiku-20240307.csv", "Jaspreet", "claude-3-haiku"),
    ("llm_sikh_bias_responses_Narveer_claude-3-haiku-20240307_adjusted_20250708_175346.csv", "Narveer", "claude-3-haiku"),
]


def load_rater_data():
    """Load all rater CSV files and merge into single DataFrame."""
    dfs = []

    for filename, rater_name, model_name in RATER_FILES:
        filepath = os.path.join(RATER_DATA_DIR, filename)

        if not os.path.exists(filepath):
            print(f"⚠️  Missing file: {filepath}")
            continue

        try:
            df = pd.read_csv(filepath)

            # Standardize column names (may vary across files)
            df.columns = df.columns.str.strip().str.lower()

            # Keep only rating columns we need
            rating_cols = ['accuracy', 'relevance', 'fairness', 'neutrality', 'representation']

            # Check which columns exist
            available_cols = [col for col in rating_cols if col in df.columns]

            # Extract key columns
            extracted = pd.DataFrame()

            # Prompt identifier
            if 'prompt_id' in df.columns:
                extracted['prompt_id'] = df['prompt_id']
            elif 'prompt' in df.columns and df['prompt'].dtype == 'object':
                # Use stable MD5 hash of prompt text as ID if explicit ID missing
                # (avoids Python's non-deterministic hash() function)
                import hashlib
                extracted['prompt_id'] = df['prompt'].apply(
                    lambda x: int(hashlib.md5(str(x).encode()).hexdigest(), 16) % 100000
                )
            else:
                extracted['prompt_id'] = range(len(df))

            # Add metadata
            extracted['rater'] = rater_name
            extracted['model'] = model_name

            # Add ratings with validation
            for col in available_cols:
                # Track non-numeric values before coercion
                original_count = len(df[col])
                extracted[col] = pd.to_numeric(df[col], errors='coerce')
                coerced_count = extracted[col].isna().sum()

                if coerced_count > 0:
                    non_numeric = original_count - coerced_count
                    if non_numeric > len(extracted) * 0.05:  # Flag if >5% were non-numeric
                        print(f"⚠️  WARNING: {filename} column '{col}': {coerced_count} values coerced to NaN")

            # Verify we have ratings
            if len(available_cols) == 0:
                print(f"⚠️  No rating columns found in {filename}")
                continue

            # Handle missing values
            missing_before = extracted[available_cols].isna().sum().sum()
            if missing_before > 0:
                print(f"   {filename}: {missing_before} missing values (will be handled in analysis)")

            dfs.append(extracted)
            print(f"✓ Loaded {filename}: {len(extracted)} rows, columns: {available_cols}")

        except Exception as e:
            print(f"✗ Error loading {filename}: {e}")

    if not dfs:
        raise ValueError("No rater data files loaded!")

    # Merge all dataframes
    combined = pd.concat(dfs, ignore_index=True)

    print(f"\n{'='*70}")
    print(f"COMBINED RATER DATA")
    print(f"{'='*70}")
    print(f"Total rows: {len(combined)}")
    print(f"Raters: {combined['rater'].nunique()} ({', '.join(combined['rater'].unique())})")
    print(f"Models: {combined['model'].nunique()} ({', '.join(combined['model'].unique())})")
    print(f"Prompts: {combined['prompt_id'].nunique()}")

    # Breakdown by model
    print(f"\nRows by model:")
    for model in combined['model'].unique():
        count = len(combined[combined['model'] == model])
        raters = combined[combined['model'] == model]['rater'].unique()
        print(f"  {model}: {count} rows ({len(raters)} raters: {', '.join(raters)})")

    return combined


def compute_summary_stats(df):
    """Compute summary statistics by model and dimension."""

    rating_cols = ['accuracy', 'relevance', 'fairness', 'neutrality', 'representation']
    rating_cols = [col for col in rating_cols if col in df.columns]

    print(f"\n{'='*70}")
    print(f"SUMMARY STATISTICS BY MODEL AND DIMENSION")
    print(f"{'='*70}")

    summary_rows = []

    for model in sorted(df['model'].unique()):
        model_data = df[df['model'] == model]
        print(f"\n{model.upper()} (n={len(model_data)}):")

        for col in rating_cols:
            if col in model_data.columns:
                valid_data = model_data[col].dropna()

                if len(valid_data) == 0:
                    print(f"  {col}: no data")
                    continue

                mean = valid_data.mean()
                std = valid_data.std()
                median = valid_data.median()
                q1 = valid_data.quantile(0.25)
                q3 = valid_data.quantile(0.75)

                print(f"  {col:15} mean={mean:.2f} (±{std:.2f}), median={median:.1f}, IQR=[{q1:.1f}, {q3:.1f}]")

                summary_rows.append({
                    'model': model,
                    'dimension': col,
                    'mean_score': round(mean, 2),
                    'std_dev': round(std, 2),
                    'median': round(median, 2),
                    'q1': round(q1, 2),
                    'q3': round(q3, 2),
                    'sample_size': len(valid_data)
                })

    return pd.DataFrame(summary_rows)


def main():
    """Load data and save results."""

    print("Loading rater evaluation data...")
    combined_df = load_rater_data()

    # Compute summary statistics
    summary_df = compute_summary_stats(combined_df)

    # Save combined data
    output_path = OUTPUT_DIR / "rater_data_combined.csv"
    combined_df.to_csv(output_path, index=False)
    print(f"\n✓ Saved combined data to {output_path}")

    # Save summary statistics
    summary_path = OUTPUT_DIR / "dimension_baselines.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"✓ Saved summary statistics to {summary_path}")

    return combined_df, summary_df


if __name__ == "__main__":
    combined, summary = main()
