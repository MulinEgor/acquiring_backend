"""Модуль для роутера транзакций с блокчейна."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import constants, dependencies
from src.modules.blockchain import schemas
from src.modules.blockchain.services.transaction_service import (
    BlockchainTransactionService,
)
from src.modules.users.models import UserModel

blockchain_transactions_router = APIRouter(
    prefix="/blockchain-transactions",
    tags=["Транзакции блокчейна"],
)


# MARK: Get
@blockchain_transactions_router.get(
    "/me",
    summary="Получить мои транзакции",
    status_code=status.HTTP_200_OK,
)
async def get_my_transactions(
    query_params: schemas.TransactionPaginationSchema = Query(),
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.GET_MY_BLOCKCHAIN_TRANSACTION]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
) -> schemas.TransactionListSchema:
    """
    Получить транзакции с пагинацией для текущего пользователя.

    Требуется разрешение: `получить свои транзакции блокчейна`.
    """
    return await BlockchainTransactionService.get_all(
        session=session,
        query_params=query_params,
        user_id=user.id,
    )


@blockchain_transactions_router.get(
    "/{id}",
    summary="Получить транзакцию по ID",
    status_code=status.HTTP_200_OK,
)
async def get_transaction_by_id(
    id: int,
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.GET_BLOCKCHAIN_TRANSACTION]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
) -> schemas.TransactionGetSchema:
    """
    Получить транзакцию по ID.

    Требуется разрешение: `получить транзакцию блокчейна`.
    """
    return await BlockchainTransactionService.get_by_id(
        session=session,
        id=id,
    )


@blockchain_transactions_router.get(
    "",
    summary="Получить транзакции",
    status_code=status.HTTP_200_OK,
)
async def get_transactions(
    query_params: schemas.TransactionPaginationSchema = Query(),
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.GET_BLOCKCHAIN_TRANSACTION]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
) -> schemas.TransactionListSchema:
    """
    Получить транзакции с пагинацией.

    Требуется разрешение: `получить транзакцию блокчейна`.
    """
    return await BlockchainTransactionService.get_all(
        session=session,
        query_params=query_params,
    )


# MARK: Patch
@blockchain_transactions_router.patch(
    "/{id}",
    summary="Подтвердить исходящую транзакцию по ID",
    status_code=status.HTTP_202_ACCEPTED,
)
async def confirm_transaction(
    id: int,
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.CONFIRM_PAY_OUT_BLOCKCHAIN_TRANSACTION]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Подтвердить исходящую транзакцию по ID.

    Требуется разрешение: `подтвердить исходящую транзакцию блокчейна`.
    """
    return await BlockchainTransactionService.confirm_pay_out(
        session=session,
        id=id,
    )
