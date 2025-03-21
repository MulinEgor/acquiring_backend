"""Модуль для сервисов для работы с транзакциями."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.transactions import schemas
from src.apps.transactions.model import TransactionModel
from src.apps.transactions.repository import TransactionRepository
from src.core import exceptions
from src.lib.base.service import BaseService


class TransactionService(
    BaseService[
        TransactionModel,
        schemas.TransactionCreateSchema,
        schemas.TransactionGetSchema,
        schemas.TransactionAdminPaginationSchema,
        schemas.TransactionListGetSchema,
        schemas.TransactionUpdateSchema,
    ],
):
    """Сервис для работы с транзакциями."""

    repository = TransactionRepository

    # MARK: Get
    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        id: int,
        merchant_id: int | None = None,
        trader_id: int | None = None,
    ) -> schemas.TransactionGetSchema:
        """
        Получить транзакцию по ID.

        Args:
            session (AsyncSession): Сессия для работы с БД.
            id (int): ID транзакции.
            merchant_id (int | None): ID мерчанта.
            trader_id (int | None): ID трейдера.

        Returns:
            schemas.TransactionGetSchema: Транзакция.

        Raises:
            NotFoundException: Транзакция не найдена.
        """
        transaction = await super().get_by_id(session, id)

        if merchant_id and transaction.merchant_id != merchant_id:
            raise exceptions.NotFoundException("Транзакция не найдена")

        if trader_id and transaction.trader_id != trader_id:
            raise exceptions.NotFoundException("Транзакция не найдена")

        return transaction
