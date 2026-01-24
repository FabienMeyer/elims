"""ELIMS Common Package - Logger Module."""

import sys

from loguru import logger


def configure_logging() -> None:
    """Configure Loguru for application-wide logging.

    This setup removes the default handler and adds a new, colorful handler
    that writes to standard error, optimized for asynchronous environments.
    """
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
        enqueue=True,
    )
    logger.info("Loguru configured successfully.")
