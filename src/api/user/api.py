"""Модуль для API мерчанта."""

from fastapi import FastAPI

from src.api.common.api import get_api
from src.api.user.routers.merchant.router import router as merchant_router
from src.api.user.routers.merchant.transactions_router import (
    router as merchant_transactions_router,
)
from src.api.user.routers.support.blockchain_router import (
    router as support_blockchain_router,
)
from src.api.user.routers.trader.blockchain_router import (
    router as trader_blockchain_router,
)
from src.api.user.routers.trader.requisites_router import (
    router as trader_requisites_router,
)
from src.api.user.routers.trader.router import router as trader_router
from src.api.user.routers.trader.transactions_router import (
    router as trader_transactions_router,
)


def include_routers(api: FastAPI) -> None:
    """Подключение роутеров"""

    for router in [
        trader_router,
        trader_blockchain_router,
        trader_requisites_router,
        trader_transactions_router,
        merchant_router,
        merchant_transactions_router,
        support_blockchain_router,
    ]:
        api.include_router(router)


api = get_api(title="API мерчанта")

include_routers(api)
