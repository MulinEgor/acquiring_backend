"""Основной модуль для конфигурации FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core import constants
from src.core.logger import configure_logger
from src.core.settings import settings
from src.modules.auth.router import auth_router
from src.modules.healthcheck.router import health_check_router
from src.modules.permissions.router import permissions_router
from src.modules.traders.router import traders_router
from src.modules.users.router import users_router
from src.modules.wallets.router import wallets_router

configure_logger()


app = FastAPI(
    title="Бэкенд для системы эквайринга",
    version=settings.APP_VERSION,
)


app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=constants.CORS_METHODS,
    allow_headers=constants.CORS_HEADERS,
)


available_routers = [
    health_check_router,
    auth_router,
    users_router,
    permissions_router,
    wallets_router,
    traders_router,
]

for router in available_routers:
    app.include_router(router=router, prefix="/api/v1")
