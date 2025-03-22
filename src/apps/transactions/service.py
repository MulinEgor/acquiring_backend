"""Модуль для сервисов для работы с транзакциями."""

from typing import Literal

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.transactions import schemas
from src.apps.transactions.model import TransactionModel, TransactionTypeEnum
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

        logger.info(
            "Получение транзакции с ID: {} для мерчанта с ID: {} и трейдера с ID: {}",
            id,
            merchant_id,
            trader_id,
        )

        transaction = await super().get_by_id(session, id)

        if merchant_id and transaction.merchant_id != merchant_id:
            raise exceptions.NotFoundException("Транзакция не найдена")

        if trader_id and transaction.trader_id != trader_id:
            raise exceptions.NotFoundException("Транзакция не найдена")

        return transaction

    @classmethod
    async def get_pending_by_user_id(
        cls,
        session: AsyncSession,
        user_id: int,
        type: TransactionTypeEnum,
        role: Literal["merchant", "trader"],
    ) -> schemas.TransactionGetSchema:
        """
        Получить транзакцию в процессе обработки.

        Args:
            session: Сессия базы данных.
            user_id: Идентификатор пользователя.
            type: Тип транзакции.
            role: Роль пользователя.

        Returns:
            Транзакция.

        Raises:
            NotFoundException: Транзакция не найдена.
        """

        transaction = await cls.repository.get_pending_by_user_id(
            session=session,
            user_id=user_id,
            type=type,
            role=role,
        )

        if not transaction:
            raise exceptions.NotFoundException("Транзакция не найдена")

        return transaction
