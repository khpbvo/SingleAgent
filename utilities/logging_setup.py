"""Centralized logging configuration for the project."""

from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler

# Internal flag to avoid reconfiguring the root logger multiple times
_ROOT_CONFIGURED = False


def setup_logging(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Configure logging for the given module name.

    This function configures the root logger on first use and creates a
    rotating file handler for the specified logger. The logger is returned so
    callers can further customize if needed.

    Parameters
    ----------
    name:
        Name of the logger to configure. Typically ``__name__`` of the calling
        module.
    level:
        Logging level for both the root and child loggers. Defaults to
        ``logging.DEBUG``.
    """

    global _ROOT_CONFIGURED

    os.makedirs("logs", exist_ok=True)

    # Configure the root logger only once
    root_logger = logging.getLogger()
    if not _ROOT_CONFIGURED:
        root_logger.setLevel(level)
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        _ROOT_CONFIGURED = True

    # Create and configure the child logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = RotatingFileHandler(
            f"logs/{name}.log", maxBytes=10 * 1024 * 1024, backupCount=3
        )
        handler.setLevel(level)
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        logger.addHandler(handler)
        logger.propagate = False

    return logger


__all__ = ["setup_logging"]

