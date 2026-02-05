"""Local runner for the na-emailer Functions Framework service.
Usage:
  python start.py
Environment:
  - PORT: server port (default: 8080)
  - Any NA_* variables (see README.md)
This is meant for local development only; Knative should run the container.
"""
from __future__ import annotations
import logging
import os
import subprocess
import sys


logger = logging.getLogger("na_emailer.start")


def _configure_logging() -> None:
    #keep it simple and consistent with app/main.py
    level_name = os.getenv("NA_LOG_LEVEL", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def main() -> int:
    _configure_logging()
    os.environ.setdefault("PYTHONPATH", os.getcwd())

    #"nice" local defaults
    os.environ.setdefault("PORT", "8080")
    os.environ.setdefault("NA_LOG_LEVEL", "INFO")

    #default to dry-run locally so you don't accidentally email people.
    os.environ.setdefault("NA_DRY_RUN", "true")

    host = os.getenv("HOST", "0.0.0.0")
    port = os.environ["PORT"]

    logger.info("Starting na-emailer (local dev runner)")
    logger.info("Dry-run mode: %s", os.environ.get("NA_DRY_RUN"))
    logger.info("Listening on http://%s:%s/", host, port)
    logger.info("Waiting for CloudEvents...")

    #very hacky way to start functions framework; todo: improve
    cmd = [
        sys.executable,
        "-m",
        "functions_framework",
        "--source",
        os.path.join("app", "main.py"),
        "--target",
        "handle",
        "--host",
        host,
        "--port",
        port,
    ]
    rc = subprocess.call(cmd)
    if rc != 0:
        logger.error("Functions Framework exited with code %s", rc)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
