"""Сервис для работы с транзакциями на блокчейне."""

import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.core import exceptions
from src.core.base.service import BaseService
from src.modules.blockchain import schemas
from src.modules.blockchain.models import BlockchainTransactionModel, StatusEnum
from src.modules.blockchain.repository import BlockchainTransactionRepository


class BlockchainTransactionService(
    BaseService[
        BlockchainTransactionModel,
        schemas.TransactionCreateSchema,
        schemas.TransactionGetSchema,
        schemas.TransactionPaginationSchema,
        schemas.TransactionListSchema,
        schemas.TransactionUpdateSchema,
    ]
):
    """Сервис для работы с транзакциями на блокчейне."""

    repository = BlockchainTransactionRepository

    @classmethod
    async def update_status_by_id(
        cls,
        session: AsyncSession,
        id: int,
        status: StatusEnum,
    ) -> None:
        """
        Обновить статус транзакции по хэшу.

        Args:
            session: Сессия базы данных.
            id: Идентификатор транзакции.
            status: Статус транзакции.

        Raises:
            NotFoundException: Транзакция не найдена.
        """

        transaction_db = await cls.repository.get_one_or_none(
            session=session,
            id=id,
        )

        if not transaction_db:
            raise exceptions.NotFoundException("Транзакция не найдена.")

        transaction_db.status = status
        await session.commit()

    @classmethod
    async def get_pending_by_user_id(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> BlockchainTransactionModel:
        """
        Получить транзакцию по идентификатору пользователя.
        У пользователя в один момент времени может быть только одна транзакция,
            которая в процессе обработки.

        Args:
            session: Сессия базы данных.
            user_id: Идентификатор пользователя.

        Returns:
            Транзакция.

        Raises:
            NotFoundException: Транзакция не найдена или просрочена.
        """

        transaction_db = await cls.repository.get_one_or_none(
            session=session,
            user_id=user_id,
            status=StatusEnum.PENDING,
        )

        if not transaction_db:
            raise exceptions.NotFoundException("Транзакций в процессе обработки нет.")

        elif transaction_db.expires_at < datetime.now():
            await cls.update_status_by_id(
                session=session,
                id=transaction_db.id,
                status=StatusEnum.FAILED,
            )

            raise exceptions.NotFoundException(
                "Транзакция в процессе обработки просрочена."
            )

        return transaction_db
