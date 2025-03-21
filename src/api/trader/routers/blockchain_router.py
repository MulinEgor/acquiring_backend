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
