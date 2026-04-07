"""presidio-hardened-ids: ML-based intrusion detection with adversarial hardening."""

from .adversarial import EvasionReport, load_adversarial_flows, run_evasion
from .detector import DetectorMetrics, IsolationForestDetector
from .features import get_X, get_y, load, summary
from .security import log_security_event, run_dependency_audit, setup_logging
from .traffic import FEATURE_COLS, generate, stream_flow

__version__ = "0.1.0"
__all__ = [
    "generate",
    "stream_flow",
    "FEATURE_COLS",
    "load",
    "get_X",
    "get_y",
    "summary",
    "IsolationForestDetector",
    "DetectorMetrics",
    "run_evasion",
    "EvasionReport",
    "load_adversarial_flows",
    "setup_logging",
    "log_security_event",
    "run_dependency_audit",
]

setup_logging()
