"""
Logging configuration and utilities
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from ...config.settings import settings


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """
    Setup application logging configuration

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        format_string: Custom log format (optional)

    Returns:
        Configured logger instance
    """
    level = level or settings.log_level
    log_file = log_file or settings.log_file

    format_string = format_string or (
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    # Configure root logger
    logger = logging.getLogger("pdftool")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_formatter = logging.Formatter(format_string)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setLevel(getattr(logging, level.upper()))
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return logging.getLogger(f"pdftool.{name}")
