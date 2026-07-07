"""
Utility helpers for the Enterprise GenAI Platform.
"""

import logging
import sys
from typing import Any


def setup_basic_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Sets up a standardized basic stdout logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
