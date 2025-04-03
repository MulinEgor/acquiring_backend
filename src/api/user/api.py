"""Модуль для API пользователя."""

from fastapi import FastAPI

from src.api.common.api import get_api
from src.api.common.routers.disputes_router import router as disputes_router
from src.api.user.routers.merchants.router import router as merchant_router
from src.api.user.routers.support.blockchain_router import (
    router as support_blockchain_router,
)
from src.api.user.routers.support.disputes_router import (
    router as support_dispute_router,
)
from src.api.user.routers.traders.router import router as trader_router
from src.api.user.routers.users.blockchain_router import (
    router as blockchain_router,
)
from src.api.user.routers.users.requisites_router import (
    router as requisites_router,
)
from src.api.user.routers.users.router import router as user_router
from src.api.user.routers.users.transactions_router import (
    router as transactions_router,
)


def include_routers(api: FastAPI) -> None:
    """Подключение роутеров"""

    for router in [
        user_router,
        trader_router,
        merchant_router,
        blockchain_router,
        requisites_router,
        transactions_router,
        support_blockchain_router,
        disputes_router,
        support_dispute_router,
    ]:
        api.include_router(router)


api = get_api(title="API пользователя")

include_routers(api)
