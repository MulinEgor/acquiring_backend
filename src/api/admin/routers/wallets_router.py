"""Модуль для админского роутера кошельков."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.wallets import schemas
from src.apps.wallets.service import WalletService
from src.core import constants, dependencies

router = APIRouter(prefix="/wallets", tags=["Кошельки"])


# MARK: Post
@router.post(
    "",
    summary="Создать кошелек",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.CREATE_WALLET]
            )
        ),
    ],
)
async def create_wallet_route(
    data: schemas.WalletCreateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    return await WalletService.create(session, data)


# MARK: Get
@router.get(
    "/{address}",
    summary="Получить данные кошелька по адресу.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.GET_WALLET])
        ),
    ],
)
async def get_wallet_by_address_route(
    address: str,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить данные кошелька по адресу.

    Требуется разрешение: `получить кошелек`.
    """
    return await WalletService.get_by_address(session, address)


@router.get(
    "",
    summary="Получить список кошельков.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.GET_WALLET])
        ),
    ],
)
async def get_wallets_by_admin_route(
    query_params: schemas.WalletPaginationSchema = Query(),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить список кошельков.

    Требуется разрешение: `получить кошелек`.
    """
    return await WalletService.get_all(session, query_params)


# MARK: Delete
@router.delete(
    "/{address}",
    summary="Удалить кошелек по адресу.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.DELETE_WALLET]
            )
        ),
    ],
)
async def delete_wallet_by_address_route(
    address: str,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Удалить кошелек по адресу.

    Требуется разрешение: `удалить кошелек`.
    """
    return await WalletService.delete_by_address(session, address)
