"""Модуль для роутера транзакций блокчейна."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.blockchain import schemas
from src.apps.blockchain.services.transaction_service import (
    BlockchainTransactionService,
)
from src.apps.users.model import UserModel
from src.core import constants, dependencies

router = APIRouter(
    prefix="/blockchain-transactions",
    tags=["Транзакции блокчейна"],
)


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить свою транзакцию по ID",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.GET_MY_BLOCKCHAIN_TRANSACTION]
            )
        ),
    ],
)
async def get_transaction_by_id_route(
    id: int,
    user: UserModel = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
) -> schemas.TransactionGetSchema:
    """
    Получить транзакцию по ID.

    Требуется разрешение: `получить свою транзакцию блокчейна`.
    """
    return await BlockchainTransactionService.get_by_id(
        session=session,
        id=id,
        user_id=user.id,
    )


@router.get(
    "",
    summary="Получить свои транзакции.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.GET_MY_BLOCKCHAIN_TRANSACTION]
            )
        ),
    ],
)
async def get_my_transactions_route(
    query_params: schemas.TransactionPaginationSchema = Query(),
    user: UserModel = Depends(dependencies.get_current_user),
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
