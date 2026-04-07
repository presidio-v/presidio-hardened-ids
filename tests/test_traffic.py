"""Tests for synthetic traffic generator."""

import pandas as pd
import pytest

from presidio_ids.traffic import FEATURE_COLS, LABEL_COL, generate, stream_flow


def test_generate_shape():
    df = generate(n_normal=100, n_attacks=10, seed=1)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 100  # attacks rounded per type; at least normal rows present


def test_generate_columns():
    df = generate(n_normal=50, n_attacks=5, seed=1)
    for col in FEATURE_COLS:
        assert col in df.columns
    assert LABEL_COL in df.columns


def test_generate_label_counts():
    df = generate(n_normal=100, n_attacks=30, attack_types=["portscan"], seed=2)
    assert df[LABEL_COL].sum() >= 1
    assert (df[LABEL_COL] == 0).sum() == 100


def test_generate_invalid_attack_type():
    with pytest.raises(ValueError):
        generate(n_normal=10, n_attacks=5, attack_types=["unknown"])


def test_generate_reproducible():
    df1 = generate(n_normal=50, n_attacks=5, seed=42)
    df2 = generate(n_normal=50, n_attacks=5, seed=42)
    assert df1.equals(df2)


def test_generate_different_seeds():
    df1 = generate(n_normal=50, n_attacks=5, seed=1)
    df2 = generate(n_normal=50, n_attacks=5, seed=2)
    assert not df1.equals(df2)


def test_stream_flow_returns_dict():
    flow = stream_flow(attack_prob=0.0)
    for col in FEATURE_COLS:
        assert col in flow


def test_stream_flow_attack_when_prob_1():
    flow = stream_flow(attack_prob=1.0, seed=0)
    assert flow[LABEL_COL] == 1
