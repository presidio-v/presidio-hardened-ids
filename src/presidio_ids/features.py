"""Feature engineering: load CSV, validate schema, return X / y arrays."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .traffic import FEATURE_COLS, LABEL_COL


def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = set(FEATURE_COLS) - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    return df


def get_X(df: pd.DataFrame) -> np.ndarray:
    return df[FEATURE_COLS].to_numpy(dtype=float)


def get_y(df: pd.DataFrame) -> np.ndarray:
    if LABEL_COL not in df.columns:
        return np.zeros(len(df), dtype=int)
    return df[LABEL_COL].to_numpy(dtype=int)


def summary(df: pd.DataFrame) -> dict:
    n = len(df)
    n_attack = int(df[LABEL_COL].sum()) if LABEL_COL in df.columns else 0
    n_normal = n - n_attack
    return {
        "total_flows": n,
        "normal_flows": n_normal,
        "attack_flows": n_attack,
        "attack_ratio": round(n_attack / n, 4) if n else 0.0,
        "features": FEATURE_COLS,
        "n_features": len(FEATURE_COLS),
    }
