"""Модуль для роутера транзакций с блокчейна."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.blockchain import schemas
from src.apps.blockchain.services.transaction_service import (
    BlockchainTransactionService,
)
from src.core import constants, dependencies

router = APIRouter(
    prefix="/blockchain-transactions",
    tags=["Транзакции блокчейна"],
)


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить транзакцию по ID",
    status_code=status.HTTP_200_OK,
)
async def get_transaction_by_id_route(
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


@router.get(
    "",
    summary="Получить транзакции",
    status_code=status.HTTP_200_OK,
)
async def get_transactions_route(
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
@router.patch(
    "/{id}",
    summary="Подтвердить исходящую транзакцию по ID",
    status_code=status.HTTP_202_ACCEPTED,
)
async def confirm_transaction_route(
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
