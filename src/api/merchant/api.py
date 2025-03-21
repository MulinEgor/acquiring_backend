"""Модуль для API мерчанта."""

from fastapi import FastAPI

from src.api.common.api import get_api
from src.api.merchant.routers.blockchain_router import router as blockchain_router


def include_routers(api: FastAPI) -> None:
    """Подключение роутеров"""
    for router in [blockchain_router]:
        api.include_router(router)


api = get_api(title="API мерчанта")
include_routers(api)
