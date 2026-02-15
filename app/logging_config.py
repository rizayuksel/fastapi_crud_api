"""
Logging configuration.

Simple setup to track startup, shutdown, and errors.
"""

import logging
import sys


def setup_logging():
    """Configure application logging"""

    # Basic configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Get app logger
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)

    return logger
