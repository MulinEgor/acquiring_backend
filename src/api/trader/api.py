"""Модуль для API трейдера."""

from fastapi import FastAPI

from src.api.common.api import get_api
from src.api.trader.routers.requisites_router import router as trader_requisites_router
from src.api.trader.routers.router import router as trader_router


def include_routers(api: FastAPI) -> None:
    """Подключение роутеров"""
    for router in [trader_router, trader_requisites_router]:
        api.include_router(router)


api = get_api(title="API трейдера")
include_routers(api)
