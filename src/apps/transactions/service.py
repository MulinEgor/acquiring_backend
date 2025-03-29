"""Модуль для сервисов для работы с транзакциями."""

from loguru import logger
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
        user_id: int | None = None,
    ) -> schemas.TransactionGetSchema:
        """
        Получить транзакцию по ID.

        Args:
            session (AsyncSession): Сессия для работы с БД.
            id (int): ID транзакции.
            merchant_id (int | None): ID мерчанта.
            trader_id (int | None): ID трейдера.

        Returns:
            TransactionGetSchema: Транзакция.

        Raises:
            NotFoundException: Транзакция не найдена.
        """

        logger.info(
            "Получение транзакции с ID: {} для пользователя с ID: {}",
            id,
            user_id,
        )

        transaction = await super().get_by_id(session, id)

        if user_id and (
            transaction.merchant_id != user_id and transaction.trader_id != user_id
        ):
            raise exceptions.NotFoundException("Транзакция не найдена")

        return transaction
