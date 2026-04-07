"""Adversarial evasion attack and adversarial retraining.

Evasion strategy: hill-climbing perturbation.
For each attack flow, repeatedly nudge feature values toward the normal distribution
until the anomaly score rises above the detector threshold (evasion success) or
the attempt budget is exhausted.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .detector import IsolationForestDetector
from .features import FEATURE_COLS, get_X
from .security import log_security_event
from .traffic import LABEL_COL, generate


@dataclass
class EvasionResult:
    attempt: int
    original_score: float
    final_score: float
    evaded: bool
    n_perturbations: int
    attack_type: str


@dataclass
class EvasionReport:
    model_path: str
    attack_type: str
    n_attempts: int
    n_evaded: int
    evasion_rate: float
    evaded_flows: list[dict]


def _perturb_toward_normal(
    flow: np.ndarray,
    normal_mean: np.ndarray,
    normal_std: np.ndarray,
    rng: np.random.Generator,
    step: float = 0.1,
) -> np.ndarray:
    noise = rng.normal(0, normal_std * step)
    direction = normal_mean - flow
    perturbed = flow + direction * step + noise * 0.05
    perturbed = np.clip(perturbed, 0, None)
    return perturbed


def run_evasion(
    model_path: str,
    attack_type: str = "portscan",
    n_attempts: int = 200,
    max_perturbations: int = 50,
    seed: int = 42,
    output: str | None = None,
) -> EvasionReport:
    detector = IsolationForestDetector.load(model_path)
    rng = np.random.default_rng(seed)

    normal_df = generate(n_normal=1000, n_attacks=0, seed=seed)
    normal_X = get_X(normal_df)
    normal_mean = normal_X.mean(axis=0)
    normal_std = normal_X.std(axis=0) + 1e-6

    attack_df = generate(n_normal=0, n_attacks=n_attempts, attack_types=[attack_type], seed=seed)
    attack_X = get_X(attack_df)

    results: list[EvasionResult] = []
    evaded_flows: list[dict] = []

    for i in range(min(n_attempts, len(attack_X))):
        flow = attack_X[i].copy()
        orig_score = float(detector.score_samples(flow.reshape(1, -1))[0])
        threshold = detector._threshold
        evaded = orig_score >= threshold
        n_perturb = 0

        if not evaded:
            for _ in range(max_perturbations):
                flow = _perturb_toward_normal(flow, normal_mean, normal_std, rng)
                score = float(detector.score_samples(flow.reshape(1, -1))[0])
                n_perturb += 1
                if score >= threshold:
                    evaded = True
                    break

        final_score = float(detector.score_samples(flow.reshape(1, -1))[0])
        result = EvasionResult(
            attempt=i,
            original_score=round(orig_score, 6),
            final_score=round(final_score, 6),
            evaded=evaded,
            n_perturbations=n_perturb,
            attack_type=attack_type,
        )
        results.append(result)
        if evaded:
            flow_dict = dict(zip(FEATURE_COLS, flow.tolist(), strict=True))
            flow_dict[LABEL_COL] = 1
            evaded_flows.append(flow_dict)

    n_evaded = sum(r.evaded for r in results)
    evasion_rate = round(n_evaded / len(results), 4) if results else 0.0

    report = EvasionReport(
        model_path=model_path,
        attack_type=attack_type,
        n_attempts=len(results),
        n_evaded=n_evaded,
        evasion_rate=evasion_rate,
        evaded_flows=evaded_flows,
    )

    if output:
        pathlib.Path(output).parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            json.dump(asdict(report), f, indent=2)

    log_security_event(
        "evasion_complete",
        model=model_path,
        attack_type=attack_type,
        n_evaded=n_evaded,
        evasion_rate=evasion_rate,
    )
    return report


def load_adversarial_flows(report_path: str) -> pd.DataFrame:
    with open(report_path) as f:
        data = json.load(f)
    flows = data.get("evaded_flows", [])
    if not flows:
        return pd.DataFrame(columns=FEATURE_COLS + [LABEL_COL])
    return pd.DataFrame(flows)
