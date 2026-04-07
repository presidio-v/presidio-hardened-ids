# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes    |

## Reporting a Vulnerability

Do not open a public GitHub issue for security vulnerabilities.

Email **security@presidio-group.eu** with description, reproduction steps, and impact.
Acknowledgement within 48 hours; resolution within 7 days.

## Security Features

| Feature | Description |
|---|---|
| **Input validation** | All CLI parameters are type-checked and bounds-validated |
| **No shell execution** | All computation is pure Python/NumPy/sklearn; no subprocess calls |
| **Dependency audit** | `pip-audit` runs on import (non-blocking) |
| **Security event logging** | Structured events for fit, evaluate, save, load, and evasion |
| **No network I/O** | Traffic is synthetic; dashboard reads local files only |
| **Deterministic generation** | All random operations accept a seed for reproducibility |
