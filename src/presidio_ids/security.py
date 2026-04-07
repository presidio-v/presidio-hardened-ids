"""Security utilities: structured logging and dependency audit."""

from __future__ import annotations

import logging
import subprocess
import sys

logger = logging.getLogger("presidio_ids")


def setup_logging(level: int = logging.INFO) -> None:
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(level)


def log_security_event(event: str, **kwargs: object) -> None:
    parts = " ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info("SECURITY_EVENT event=%s %s", event, parts)


def run_dependency_audit() -> None:
    try:
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "pip_audit", "--progress-spinner=off", "-q"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            logger.warning("pip-audit found issues:\n%s", result.stdout or result.stderr)
        else:
            logger.debug("pip-audit: no vulnerabilities found")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.debug("pip-audit not available; skipping dependency check")
