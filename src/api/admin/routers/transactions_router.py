"""Модуль для роутера админа для работы с транзакциями."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.transactions import schemas
from src.apps.transactions.service import TransactionService
from src.core import dependencies
from src.core.constants import PermissionEnum
from src.core.dependencies import get_session

router = APIRouter(prefix="/transactions", tags=["Транзакции"])


# MARK: Post
@router.post(
    "",
    summary="Создать транзакцию.",
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction_route(
    body: schemas.TransactionCreateSchema,
    _: bool = Depends(
        dependencies.check_user_permissions([PermissionEnum.CREATE_TRANSACTION])
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Создать транзакцию.

    Требуется разрешение: `создать транзакцию`.
    """
    return await TransactionService.create(
        session=session,
        data=body,
    )


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить транзакцию по ID.",
    status_code=status.HTTP_200_OK,
)
async def get_transaction_route(
    id: int,
    _: bool = Depends(
        dependencies.check_user_permissions([PermissionEnum.GET_TRANSACTION])
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить транзакцию по ID.

    Требуется разрешение: `получить транзакцию`.
    """
    return await TransactionService.get_by_id(
        session=session,
        id=id,
    )


@router.get(
    "",
    summary="Получить все транзакции.",
    status_code=status.HTTP_200_OK,
)
async def get_transactions_route(
    query_params: schemas.TransactionAdminPaginationSchema = Query(),
    _: bool = Depends(
        dependencies.check_user_permissions([PermissionEnum.GET_TRANSACTION])
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить все реквизиты.

    Требуется разрешение: `получить транзакции`.
    """
    return await TransactionService.get_all(
        session=session,
        query_params=query_params,
    )


# MARK: Put
@router.put(
    "/{id}",
    summary="Обновить транзакцию по ID.",
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_transaction_route(
    id: int,
    body: schemas.TransactionUpdateSchema,
    _: bool = Depends(
        dependencies.check_user_permissions([PermissionEnum.UPDATE_TRANSACTION])
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Обновить транзакцию по ID.

    Требуется разрешение: `обновить транзакцию`.
    """
    return await TransactionService.update(
        session=session,
        id=id,
        data=body,
    )


# MARK: Delete
@router.delete(
    "/{id}",
    summary="Удалить транзакцию по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_transaction_route(
    id: int,
    _: bool = Depends(
        dependencies.check_user_permissions([PermissionEnum.DELETE_TRANSACTION])
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Удалить транзакцию по ID.

    Требуется разрешение: `удалить транзакцию`.
    """
    return await TransactionService.delete(
        session=session,
        id=id,
    )
