"""Tests for feature engineering."""

import pytest

from presidio_ids.features import FEATURE_COLS, get_X, get_y, load, summary


def test_get_X_shape(small_df):
    X = get_X(small_df)
    assert X.shape == (len(small_df), len(FEATURE_COLS))


def test_get_X_dtype(small_df):
    X = get_X(small_df)
    assert X.dtype == float


def test_get_y_values(small_df):
    y = get_y(small_df)
    assert set(y).issubset({0, 1})
    assert len(y) == len(small_df)


def test_summary(small_df):
    stats = summary(small_df)
    assert stats["total_flows"] == len(small_df)
    assert stats["normal_flows"] + stats["attack_flows"] == stats["total_flows"]
    assert stats["n_features"] == len(FEATURE_COLS)


def test_load(tmp_path, small_df):
    path = str(tmp_path / "traffic.csv")
    small_df.to_csv(path, index=False)
    df = load(path)
    assert list(df.columns) == list(small_df.columns)


def test_load_missing_columns(tmp_path):
    import pandas as pd

    df = pd.DataFrame({"col1": [1, 2]})
    path = str(tmp_path / "bad.csv")
    df.to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        load(path)
