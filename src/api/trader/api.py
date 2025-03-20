"""Модуль для API трейдера."""

from fastapi import FastAPI

from src.api.common.api import get_api
from src.api.trader.router.router import router as trader_router


def include_routers(api: FastAPI) -> None:
    """Подключение роутеров"""
    api.include_router(trader_router)


api = get_api(title="API трейдера")
include_routers(api)
