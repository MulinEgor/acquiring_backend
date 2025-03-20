"""Основной модуль для конфигурации FastAPI."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from src.core import constants, handlers, middlewares
from src.core.logger import setup_logging
from src.core.settings import settings
from src.modules.auth.router import auth_router
from src.modules.healthcheck.router import health_check_router
from src.modules.permissions.router import permissions_router
from src.modules.traders.router import traders_router
from src.modules.users.router import users_router
from src.modules.wallets.router import wallets_router


def setup_middlewares(app: FastAPI):
    """Настройка middlewares"""
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=constants.CORS_METHODS,
        allow_headers=constants.CORS_HEADERS,
    )
    app.add_middleware(middlewares.ORJSONRequestMiddleware)


def setup_exception_handlers(app: FastAPI):
    """Настройка обработчиков исключений"""
    app.add_exception_handler(HTTPException, handlers.http_exception_handler)
    app.add_exception_handler(Exception, handlers.exception_handler)


def include_routers(app: FastAPI):
    """Подключение роутеров"""
    available_routers = [
        health_check_router,
        auth_router,
        users_router,
        permissions_router,
        wallets_router,
        traders_router,
    ]

    for router in available_routers:
        app.include_router(router, prefix="/api")


app = FastAPI(
    title="Бэкенд для системы эквайринга",
    version=settings.APP_VERSION,
    default_response_class=ORJSONResponse,
)

setup_logging()
setup_middlewares(app)
setup_exception_handlers(app)
include_routers(app)
