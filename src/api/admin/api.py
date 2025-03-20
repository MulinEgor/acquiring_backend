"""Модуль для API админа."""

from fastapi import FastAPI

from src.api.admin.routers.permissions_router import router as permissions_router
from src.api.admin.routers.users_router import router as users_router
from src.api.admin.routers.wallets_router import router as wallets_router
from src.api.common.api import get_api
from src.api.common.routers.blockchain_router import router as blockchain_router


def include_routers(api: FastAPI) -> None:
    """Подключение роутеров"""
    api.include_router(users_router)
    api.include_router(permissions_router)
    api.include_router(wallets_router)
    api.include_router(blockchain_router)


api = get_api(title="API админа")
include_routers(api)
