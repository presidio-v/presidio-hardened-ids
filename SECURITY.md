# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Yes    |

## Reporting a Vulnerability

Please report security vulnerabilities by opening a private GitHub Security Advisory
(via the "Security" tab → "Report a vulnerability") rather than a public issue.

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You will receive an acknowledgement within 5 business days. We aim to release a patch
within 30 days of a confirmed vulnerability.

## Security Features

| Feature | Description |
|---|---|
| **Input validation** | All CLI parameters are type-checked and bounds-validated |
| **No shell execution** | All computation is pure Python/NumPy/sklearn; no subprocess calls |
| **Dependency audit** | `pip-audit` runs on import (non-blocking) |
| **Security event logging** | Structured events for fit, evaluate, save, load, and evasion |
| **No network I/O** | Traffic is synthetic; dashboard reads local files only |
| **Deterministic generation** | All random operations accept a seed for reproducibility |

## Software Development Lifecycle

This repository is developed under the Presidio hardened-family SDLC. The public report
— scope, standards mapping, threat-model gates, and supply-chain controls — is at
<https://github.com/presidio-v/presidio-hardened-docs/blob/main/sdlc/sdlc-report.md>.
