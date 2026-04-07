"""Synthetic network traffic generator.

Produces a CSV with realistic-looking flow features for normal and attack traffic.
Attack types: portscan, synflood, exfiltration.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Feature columns used throughout the package
FEATURE_COLS = [
    "duration_s",
    "packet_count",
    "byte_count",
    "avg_packet_size",
    "inter_arrival_ms",
    "syn_flag_ratio",
    "rst_flag_ratio",
    "unique_dst_ports",
    "dst_port",
    "protocol",
]
LABEL_COL = "label"  # 0 = normal, 1 = attack


def _normal_flow(rng: np.random.Generator) -> dict:
    duration = rng.exponential(30.0)
    packets = int(rng.lognormal(4.0, 1.2))
    return {
        "duration_s": round(max(0.1, duration), 3),
        "packet_count": max(2, packets),
        "byte_count": max(100, int(packets * rng.lognormal(6.5, 0.8))),
        "avg_packet_size": round(rng.normal(800, 200), 1),
        "inter_arrival_ms": round(max(1.0, rng.exponential(50.0)), 2),
        "syn_flag_ratio": round(min(1.0, rng.beta(1, 20)), 4),
        "rst_flag_ratio": round(min(1.0, rng.beta(1, 50)), 4),
        "unique_dst_ports": int(rng.integers(1, 4)),
        "dst_port": int(rng.choice([80, 443, 8080, 22, 25, 587, 993, 3306, 5432])),
        "protocol": int(rng.choice([6, 17], p=[0.85, 0.15])),  # TCP / UDP
        LABEL_COL: 0,
    }


def _portscan_flow(rng: np.random.Generator) -> dict:
    n_ports = int(rng.integers(50, 1024))
    return {
        "duration_s": round(rng.uniform(0.1, 5.0), 3),
        "packet_count": n_ports,
        "byte_count": n_ports * 60,
        "avg_packet_size": 60.0,
        "inter_arrival_ms": round(rng.uniform(0.5, 3.0), 2),
        "syn_flag_ratio": round(rng.uniform(0.85, 1.0), 4),
        "rst_flag_ratio": round(rng.uniform(0.3, 0.8), 4),
        "unique_dst_ports": n_ports,
        "dst_port": int(rng.integers(1, 65535)),
        "protocol": 6,
        LABEL_COL: 1,
    }


def _synflood_flow(rng: np.random.Generator) -> dict:
    packets = int(rng.integers(5000, 50000))
    return {
        "duration_s": round(rng.uniform(1.0, 10.0), 3),
        "packet_count": packets,
        "byte_count": packets * 60,
        "avg_packet_size": 60.0,
        "inter_arrival_ms": round(rng.uniform(0.01, 0.5), 3),
        "syn_flag_ratio": round(rng.uniform(0.92, 1.0), 4),
        "rst_flag_ratio": 0.0,
        "unique_dst_ports": 1,
        "dst_port": int(rng.choice([80, 443])),
        "protocol": 6,
        LABEL_COL: 1,
    }


def _exfiltration_flow(rng: np.random.Generator) -> dict:
    packets = int(rng.integers(100, 2000))
    return {
        "duration_s": round(rng.uniform(60.0, 600.0), 3),
        "packet_count": packets,
        "byte_count": int(packets * rng.lognormal(9.0, 0.5)),
        "avg_packet_size": round(rng.normal(1400, 50), 1),
        "inter_arrival_ms": round(rng.uniform(200, 2000), 2),
        "syn_flag_ratio": round(rng.beta(2, 30), 4),
        "rst_flag_ratio": 0.0,
        "unique_dst_ports": 1,
        "dst_port": int(rng.choice([443, 8443, 9000])),
        "protocol": 6,
        LABEL_COL: 1,
    }


_ATTACK_GENERATORS = {
    "portscan": _portscan_flow,
    "synflood": _synflood_flow,
    "exfiltration": _exfiltration_flow,
}


def generate(
    n_normal: int = 10000,
    n_attacks: int = 500,
    attack_types: list[str] | None = None,
    seed: int = 42,
) -> pd.DataFrame:
    if attack_types is None:
        attack_types = ["portscan", "synflood", "exfiltration"]

    unknown = set(attack_types) - set(_ATTACK_GENERATORS)
    if unknown:
        raise ValueError(f"Unknown attack types: {unknown}. Valid: {list(_ATTACK_GENERATORS)}")

    rng = np.random.default_rng(seed)
    rows: list[dict] = []

    for _ in range(n_normal):
        rows.append(_normal_flow(rng))

    per_type = max(1, n_attacks // len(attack_types))
    for atype in attack_types:
        gen = _ATTACK_GENERATORS[atype]
        for _ in range(per_type):
            rows.append(gen(rng))

    df = pd.DataFrame(rows)
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return df


def stream_flow(attack_prob: float = 0.03, seed: int | None = None) -> dict:
    rng = np.random.default_rng(seed)
    if rng.random() < attack_prob:
        atype = rng.choice(list(_ATTACK_GENERATORS))
        flow = _ATTACK_GENERATORS[atype](rng)
    else:
        flow = _normal_flow(rng)
    return flow
