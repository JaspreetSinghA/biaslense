"""Tests for rater-data loading: prompt IDs must come from the files, never row order."""

import pandas as pd
import pytest

from biaslense.analysis import load_rater_data as loader

RATING_COLUMNS = ["Accuracy", "Relevance", "Fairness", "Neutrality", "Representation"]


def _write_rater_csv(path, prompt_ids):
    """Write a minimal rater CSV with a 'Prompt ID' header, as the real files use."""
    rows = [[pid, 3, 3, 3, 3, 3] for pid in prompt_ids]
    pd.DataFrame(rows, columns=["Prompt ID", *RATING_COLUMNS]).to_csv(path, index=False)


def test_prompt_ids_come_from_prompt_id_column(tmp_path, monkeypatch):
    """Two raters whose files start at different prompts must align by ID, not by row."""
    _write_rater_csv(tmp_path / "a.csv", ["COMP_01", "COMP_02", "COMP_03"])
    _write_rater_csv(tmp_path / "b.csv", ["COMP_03", "COMP_04"])
    monkeypatch.setattr(loader, "RATER_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(loader, "RATER_FILES", [("a.csv", "A", "m"), ("b.csv", "B", "m")])

    combined = loader.load_rater_data()

    ids_by_rater = combined.groupby("rater")["prompt_id"].apply(set)
    assert ids_by_rater["A"] == {"COMP_01", "COMP_02", "COMP_03"}
    assert ids_by_rater["B"] == {"COMP_03", "COMP_04"}
    assert ids_by_rater["A"] & ids_by_rater["B"] == {"COMP_03"}


def test_missing_prompt_identifier_fails_loudly(tmp_path, monkeypatch):
    """A file with no prompt identifier must raise instead of silently using row numbers."""
    pd.DataFrame([[3, 3, 3, 3, 3]], columns=RATING_COLUMNS).to_csv(tmp_path / "c.csv", index=False)
    monkeypatch.setattr(loader, "RATER_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(loader, "RATER_FILES", [("c.csv", "C", "m")])

    with pytest.raises(ValueError, match="prompt identifier"):
        loader.load_rater_data()
