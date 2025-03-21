"""Модуль для API суппорта."""

from fastapi import FastAPI

from src.api.common.api import get_api
from src.api.common.routers.blockchain_router import router as blockchain_router


def include_routers(api: FastAPI) -> None:
    """Подключение роутеров"""
    for router in [blockchain_router]:
        api.include_router(router)


api = get_api(title="API суппорта")
include_routers(api)
