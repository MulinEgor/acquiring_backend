"""Основной модуль для конфигурации FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import auth_router
from src.constants import CORS_HEADERS, CORS_METHODS
from src.healthcheck.router import health_check_router
from src.permissions.router import permissions_router
from src.settings import settings
from src.users.router import users_router

app = FastAPI(
    title="Бэкенд для системы эквайринга",
    version=settings.APP_VERSION,
)


app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)


available_routers = [
    health_check_router,
    auth_router,
    users_router,
    permissions_router,
]

for router in available_routers:
    app.include_router(router=router, prefix="/api/v1")
