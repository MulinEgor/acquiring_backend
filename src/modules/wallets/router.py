"""Модуль для работы с маршрутами кошельков."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import constants, dependencies
from src.modules.wallets import schemas
from src.modules.wallets.service import WalletService

wallets_router = APIRouter(prefix="/wallets", tags=["Кошельки"])


# MARK: Post
@wallets_router.post(
    "",
    summary="Создать кошелек",
    status_code=status.HTTP_201_CREATED,
)
async def create_wallet(
    data: schemas.WalletCreateSchema,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.CREATE_WALLET])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    return await WalletService.create(session, data)


# MARK: Get
@wallets_router.get(
    "/{address}",
    summary="Получить данные кошелька по адресу.",
    status_code=status.HTTP_200_OK,
)
async def get_wallet_by_address_route(
    address: str,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.GET_WALLET])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить данные кошелька по адресу.

    Требуется разрешение: `получить кошелек`.
    """
    return await WalletService.get_by_address(session, address)


@wallets_router.get(
    "",
    summary="Получить список кошельков.",
    status_code=status.HTTP_200_OK,
)
async def get_wallets_by_admin_route(
    query_params: schemas.WalletPaginationSchema = Query(),
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.GET_WALLET])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить список кошельков.

    Требуется разрешение: `получить кошелек`.
    """
    return await WalletService.get_all(session, query_params)


# MARK: Delete
@wallets_router.delete(
    "/{address}",
    summary="Удалить кошелек по адресу.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_wallet_by_address_route(
    address: str,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.DELETE_WALLET])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Удалить кошелек по адресу.

    Требуется разрешение: `удалить кошелек`.
    """
    return await WalletService.delete_by_address(session, address)
