import logging
import sys

from loguru import logger


def configure_logger() -> None:
    """Настройки логгера loguru."""
    logger.remove(0)
    logger.add(
        sys.stdout,
        format="<green>{level:<8}</green>  <cyan>{time:DD.MM.YYYY HH:mm:ss}</cyan>  <blue>{message}</blue>",
        level="INFO",
    )


def setup_logging():
    """Настройка Loguru как логгера по умолчанию для uvicorn."""

    configure_logger()

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn").setLevel(logging.INFO)
