from fastapi import FastAPI

from src.api.admin.routers.blockchain_router import router as blockchain_router
from src.api.admin.routers.disputes_router import router as disputes_router
from src.api.admin.routers.notifications_router import router as notifications_router
from src.api.admin.routers.permissions_router import router as permissions_router
from src.api.admin.routers.requisites_router import router as requisites_router
from src.api.admin.routers.sms_regex_router import router as sms_regex_router
from src.api.admin.routers.transactions_router import router as transactions_router
from src.api.admin.routers.users_router import router as users_router
from src.api.admin.routers.wallets_router import router as wallets_router
from src.api.common.api import get_api


def include_routers(api: FastAPI) -> None:
    for router in [
        users_router,
        permissions_router,
        wallets_router,
        requisites_router,
        blockchain_router,
        transactions_router,
        disputes_router,
        notifications_router,
        sms_regex_router,
    ]:
        api.include_router(router)


api = get_api(title="API админа")
include_routers(api)
