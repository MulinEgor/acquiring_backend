"""Обработчики исключений"""

from fastapi import HTTPException, Request
from fastapi.responses import ORJSONResponse
from loguru import logger


async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP исключение: {exc.detail}")
    return ORJSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Исключение: {exc}")
    return ORJSONResponse(
        status_code=500, content={"detail": "Внутренняя ошибка сервера"}
    )
