"""Shared fixtures."""

import pytest

from presidio_ids import IsolationForestDetector, generate, get_X


@pytest.fixture(scope="session")
def small_df():
    return generate(n_normal=300, n_attacks=30, seed=0)


@pytest.fixture(scope="session")
def fitted_detector(small_df):
    X = get_X(small_df)
    det = IsolationForestDetector(contamination=0.05, random_state=0)
    det.fit(X)
    return det
