"""Сервис для работы с транзакциями на блокчейне."""

from datetime import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import exceptions
from src.core.base.service import BaseService
from src.modules.blockchain import schemas
from src.modules.blockchain.models import (
    BlockchainTransactionModel,
    StatusEnum,
    TypeEnum,
)
from src.modules.blockchain.repository import BlockchainTransactionRepository
from src.modules.blockchain.services.tron_service import TronService
from src.modules.users.repository import UserRepository


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

    # MARK: Get
    @classmethod
    async def get_pending_by_user_id(
        cls,
        session: AsyncSession,
        user_id: int,
        type: TypeEnum,
    ) -> BlockchainTransactionModel:
        """
        Получить транзакцию по идентификатору пользователя.
        У пользователя в один момент времени может быть только одна транзакция,
            которая в процессе обработки.

        Args:
            session: Сессия базы данных.
            user_id: Идентификатор пользователя.
            type: Тип транзакции.
        Returns:
            Транзакция.

        Raises:
            NotFoundException: Транзакция не найдена или просрочена.
        """

        logger.info(
            "Получение транзакции в статусе PENDING по ID пользователя: {}, тип: {}",
            user_id,
            type,
        )

        transaction_db = await cls.repository.get_one_or_none(
            session=session,
            user_id=user_id,
            status=StatusEnum.PENDING,
            type=type,
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

    # MARK: Update
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

        logger.info("Обновление статуса транзакции по ID: {}, статус: {}", id, status)

        transaction_db = await cls.repository.get_one_or_none(
            session=session,
            id=id,
        )

        if not transaction_db:
            raise exceptions.NotFoundException("Транзакция не найдена.")

        transaction_db.status = status
        await session.commit()

    @classmethod
    async def confirm_pay_out(
        cls,
        session: AsyncSession,
        id: int,
    ) -> None:
        """
        Подтвердить вывод средств транзакции по ID.

        Проверяет статус и тип транзакции,
            создает и подписывает транзакцию на блокчейне,
            обновляет статус транзакции в БД
            и меняет баланс пользователя.

        Args:
            session: Сессия базы данных.
            id: Идентификатор транзакции.

        Raises:
            NotFoundException: Транзакция не найдена.
            BadRequestException:
                - Транзакция не в статусе PENDING.
                - Транзакция не является выводом средств.
        """

        logger.info("Подтверждение вывода средств транзакции по ID: {}", id)

        transaction_db = await cls.repository.get_one_or_none(
            session=session,
            id=id,
        )

        if not transaction_db:
            raise exceptions.NotFoundException("Транзакция не найдена.")

        err_msgs = []
        if transaction_db.status != StatusEnum.PENDING:
            err_msgs.append("не в статусе PENDING")
        elif transaction_db.type != TypeEnum.PAY_OUT:
            err_msgs.append("не является выводом средств")
        elif transaction_db.expires_at < datetime.now():
            err_msgs.append("просрочена")
        if err_msgs:
            raise exceptions.BadRequestException("Транзакция " + ", ".join(err_msgs))

        # Создание и подписание транзакции на блокчейне
        hash = await TronService.create_and_sign_transaction(
            from_address=transaction_db.from_address,
            to_address=transaction_db.to_address,
            amount=transaction_db.amount,
        )

        transaction_db.status = StatusEnum.CONFIRMED
        transaction_db.hash = hash

        user = await UserRepository.get_one_or_none(
            session=session,
            id=transaction_db.user_id,
        )

        user.balance -= transaction_db.amount
        await session.commit()
