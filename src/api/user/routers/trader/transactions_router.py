"""Роуты для транзакций трейдера."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.transactions import schemas
from src.apps.transactions.service import TransactionService
from src.apps.users.model import UserModel
from src.core import constants, dependencies

router = APIRouter(
    prefix="/traders/transactions",
    tags=["Транзакции трейдера"],
)


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить свою транзакцию по ID.",
    status_code=status.HTTP_200_OK,
)
async def get_transaction_route(
    id: int,
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.GET_MY_TRANSACTION]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить транзакцию по ID.

    Требуется разрешение: `получить свою транзакцию`.
    """
    return await TransactionService.get_by_id(session=session, id=id, trader_id=user.id)


@router.get(
    "",
    summary="Получить свои транзакции.",
    status_code=status.HTTP_200_OK,
)
async def get_transactions_route(
    query_params: schemas.TransactionPaginationSchema = Depends(),
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.GET_MY_TRANSACTION]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить транзакции с фильтрацией и пагинацией.

    Требуется разрешение: `получить свою транзакцию`.
    """
    return await TransactionService.get_all(
        session=session,
        query_params=schemas.TransactionAdminPaginationSchema(
            trader_id=user.id,
            **query_params.model_dump(),
        ),
    )
