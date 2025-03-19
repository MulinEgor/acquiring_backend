"""Модуль для настройки логгера."""

import sys

from loguru import logger


def configure_logger() -> None:
    """Настройки логгера."""
    logger.remove(0)
    logger.add(
        sys.stdout,
        format="{level:<8}  {time:DD.MM.YYYY HH:mm:ss}  {name}:{function}:{line}  {message}",
        level="INFO",
    )
