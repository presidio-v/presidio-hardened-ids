# Presidio-Hardened IDS — Requirements

## Overview

`presidio-hardened-ids` is a complete ML-based intrusion detection system for
Experiment 4 of PRES-EDU-SEC-101. It demonstrates:

1. Synthetic network traffic generation (normal + portscan/synflood/exfiltration)
2. Isolation Forest anomaly detection with precision/recall/F1 metrics
3. Real-time Streamlit dashboard fed by a background stream process
4. Adversarial evasion attack (hill-climbing perturbation toward the normal distribution)
5. Adversarial retraining to harden the detector

## Mandatory Presidio Security Extensions

- Input validation on all CLI parameters (type bounds, valid attack types)
- Security event logging for fit, evaluate, save, load, evasion, and stream operations
- On-import dependency audit via `pip-audit` (non-blocking if unavailable)
- No shell execution; all computation is pure Python/NumPy/sklearn
- Full GitHub security files: SECURITY.md, .github/dependabot.yml, .github/workflows/codeql.yml

## Technical Requirements

- Python 3.10+
- `scikit-learn>=1.4`, `pandas>=2.1`, `numpy>=1.26`, `joblib>=1.3`
- `streamlit>=1.33` for the dashboard (optional install)
- `src/presidio_ids/` layout
- pytest ≥80% coverage
- ruff lint + format enforced
- MIT License, version 0.1.0

## Version Deliberation Log

### v0.1.0 — Initial release

**Scope decision:** Isolation Forest was chosen as the anomaly detection
algorithm because it is unsupervised (does not require labelled training data),
has a clear intuition (anomalies require fewer partitions to isolate), and maps
directly to the lecture slide 17 diagram.

**Scope decision:** The evasion attack uses hill-climbing perturbation toward
the empirical normal distribution mean rather than gradient-based attacks
(FGSM, PGF). This is intentional — sklearn models are not differentiable, and
the hill-climbing approach is sufficient to demonstrate the concept without
requiring PyTorch.

**Scope decision:** The stream → dashboard communication uses a shared CSV file
(append mode) rather than Redis or a socket. This eliminates all infrastructure
dependencies and works on any laptop without additional services.

**Scope decision:** The dashboard uses `st.rerun()` for polling rather than
`st.experimental_rerun()` (deprecated in Streamlit ≥1.28).

<!-- Deliver the complete working project ready for GitHub publish. -->

## SDLC

These requirements are delivered under the family-wide Presidio SDLC:
<https://github.com/presidio-v/presidio-hardened-docs/blob/main/sdlc/sdlc-report.md>.
