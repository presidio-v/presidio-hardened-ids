"""Tests for IsolationForestDetector."""

import numpy as np
import pytest

from presidio_ids.detector import IsolationForestDetector
from presidio_ids.features import get_X, get_y


def test_fit_and_predict(small_df):
    X = get_X(small_df)
    det = IsolationForestDetector(contamination=0.05)
    det.fit(X)
    preds = det.predict(X)
    assert preds.shape == (len(X),)
    assert set(preds).issubset({0, 1})


def test_score_samples_shape(fitted_detector, small_df):
    X = get_X(small_df)
    scores = fitted_detector.score_samples(X)
    assert scores.shape == (len(X),)


def test_score_samples_before_fit_raises():
    det = IsolationForestDetector()
    X = np.random.rand(10, 10)
    with pytest.raises(RuntimeError):
        det.score_samples(X)


def test_evaluate_returns_metrics(fitted_detector, small_df):
    X = get_X(small_df)
    y = get_y(small_df)
    metrics = fitted_detector.evaluate(X, y)
    assert 0.0 <= metrics.precision <= 1.0
    assert 0.0 <= metrics.recall <= 1.0
    assert 0.0 <= metrics.f1 <= 1.0


def test_save_and_load(fitted_detector, small_df, tmp_path):
    path = str(tmp_path / "model.pkl")
    fitted_detector.save(path)
    loaded = IsolationForestDetector.load(path)
    X = get_X(small_df)
    scores_orig = fitted_detector.score_samples(X)
    scores_loaded = loaded.score_samples(X)
    np.testing.assert_array_almost_equal(scores_orig, scores_loaded)


def test_threshold_set_after_fit(small_df):
    X = get_X(small_df)
    det = IsolationForestDetector(contamination=0.05)
    det.fit(X)
    assert det._threshold < 0
