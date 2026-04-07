"""Isolation Forest anomaly detector wrapper: fit, predict, save, load."""

from __future__ import annotations

import pathlib
from dataclasses import dataclass

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import f1_score, precision_score, recall_score

from .security import log_security_event


@dataclass
class DetectorMetrics:
    n_train: int
    contamination: float
    precision: float
    recall: float
    f1: float
    threshold: float
    evasion_rate: float = 0.0


class IsolationForestDetector:
    def __init__(self, contamination: float = 0.05, random_state: int = 42) -> None:
        self.contamination = contamination
        self.random_state = random_state
        self._model: IsolationForest | None = None
        self._threshold: float = 0.0

    def fit(self, X_train: np.ndarray) -> None:
        self._model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
        )
        self._model.fit(X_train)
        scores = self._model.score_samples(X_train)
        self._threshold = float(np.percentile(scores, self.contamination * 100))
        log_security_event(
            "detector_fit", n_samples=len(X_train), contamination=self.contamination
        )

    def score_samples(self, X: np.ndarray) -> np.ndarray:
        if self._model is None:
            raise RuntimeError("Detector not fitted. Call fit() first.")
        return self._model.score_samples(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        scores = self.score_samples(X)
        return (scores < self._threshold).astype(int)

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> DetectorMetrics:
        y_pred = self.predict(X_test)
        p = float(precision_score(y_test, y_pred, zero_division=0))
        r = float(recall_score(y_test, y_pred, zero_division=0))
        f = float(f1_score(y_test, y_pred, zero_division=0))
        metrics = DetectorMetrics(
            n_train=0,
            contamination=self.contamination,
            precision=round(p, 4),
            recall=round(r, 4),
            f1=round(f, 4),
            threshold=round(self._threshold, 6),
        )
        log_security_event(
            "detector_evaluate",
            precision=metrics.precision,
            recall=metrics.recall,
            f1=metrics.f1,
        )
        return metrics

    def save(self, path: str) -> None:
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": self._model,
            "threshold": self._threshold,
            "contamination": self.contamination,
        }
        joblib.dump(payload, path)
        log_security_event("detector_saved", path=path)

    @classmethod
    def load(cls, path: str) -> IsolationForestDetector:
        payload = joblib.load(path)
        obj = cls(contamination=payload["contamination"])
        obj._model = payload["model"]
        obj._threshold = payload["threshold"]
        log_security_event("detector_loaded", path=path)
        return obj
