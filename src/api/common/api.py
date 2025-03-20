"""Основной модуль для конфигурации FastAPI."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.api.common.routers.auth_router import router as auth_router
from src.api.common.routers.health_check_router import router as health_check_router
from src.api.common.routers.users_router import router as users_router
from src.core import constants, handlers, middlewares
from src.core.logger import setup_logging
from src.core.settings import settings


def setup_middlewares(api: FastAPI):
    """Настройка middlewares."""
    api.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=constants.CORS_METHODS,
        allow_headers=constants.CORS_HEADERS,
    )
    api.add_middleware(middlewares.ORJSONRequestMiddleware)


def setup_exception_handlers(api: FastAPI):
    """Настройка обработчиков исключений."""
    api.add_exception_handler(HTTPException, handlers.http_exception_handler)
    api.add_exception_handler(Exception, handlers.exception_handler)


def include_routers(api: FastAPI) -> None:
    """Подключение роутеров."""
    api.include_router(health_check_router)
    api.include_router(users_router)
    api.include_router(auth_router)


def get_api(title: str) -> FastAPI:
    """
    Получить экземпляр FastAPI с настроенной конфигурацией.

    Returns:
        FastAPI: экземпляр FastAPI.
    """
    api = FastAPI(
        title=title,
        version=settings.APP_VERSION,
        default_response_class=ORJSONResponse,
        redoc_url=None,
    )

    setup_logging()
    setup_middlewares(api)
    setup_exception_handlers(api)
    include_routers(api)

    return api
