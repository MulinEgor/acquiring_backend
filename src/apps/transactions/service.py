"""Модуль для сервисов для работы с транзакциями."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.transactions import schemas
from src.apps.transactions.model import (
    TransactionModel,
    TransactionStatusEnum,
    TransactionTypeEnum,
)
from src.apps.transactions.repository import TransactionRepository
from src.apps.users.model import UserModel
from src.apps.users.repository import UserRepository
from src.core import constants, exceptions
from src.lib.base.service import BaseService


class TransactionService(
    BaseService[
        TransactionModel,
        schemas.TransactionCreateSchema | schemas.TransactionUpdateSchema,
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

    @classmethod
    async def update_users_balances(
        cls,
        session: AsyncSession,
        transaction_db: TransactionModel,
        trader_db: UserModel | None = None,
        merchant_db: UserModel | None = None,
    ) -> None:
        """
        Обновление балансов пользователей. (Не создает коммит транзакции)

        Args:
            session (AsyncSession): Сессия для работы с БД.
            transaction_db (TransactionModel): Транзакция.
            trader_db (UserModel | None): Тренер.
            merchant_db (UserModel | None): Мерчант.
        """

        if not trader_db:
            trader_db = await UserRepository.get_one_or_none(
                session=session,
                id=transaction_db.trader_id,
            )
            if not trader_db:
                raise exceptions.NotFoundException("Трейдер не найден")

        if not merchant_db:
            merchant_db = await UserRepository.get_one_or_none(
                session=session,
                id=transaction_db.merchant_id,
            )
            if not merchant_db:
                raise exceptions.NotFoundException("Мерчант не найден")

        if transaction_db.type == TransactionTypeEnum.PAY_IN:
            if transaction_db.status == TransactionStatusEnum.SUCCESS:
                # Разморозка и списание средств трейдера с учетом комиссии
                trader_db.balance -= int(
                    trader_db.amount_frozen
                    - trader_db.amount_frozen
                    * (
                        constants.TRADER_TRANSACTION_COMMISSION
                        - constants.PLATFORM_TRANSACTION_COMMISSION
                    )
                )

                # Пополнение баланса мерчанта с учетом комиссии
                merchant_db.balance += int(
                    transaction_db.amount
                    - transaction_db.amount
                    * (constants.MERCHANT_TRANSACTION_COMMISSION)
                )

            trader_db.amount_frozen -= transaction_db.amount

        else:
            if transaction_db.status == TransactionStatusEnum.SUCCESS:
                # Пополнение баланса трейдера с учетом комиссии
                trader_db.balance += int(
                    transaction_db.amount
                    + transaction_db.amount
                    * (
                        constants.TRADER_TRANSACTION_COMMISSION
                        - constants.PLATFORM_TRANSACTION_COMMISSION
                    )
                )

                # Разморозка и списание средств мерчанта с учетом комиссии
                merchant_db.balance -= int(
                    transaction_db.amount
                    + transaction_db.amount * constants.MERCHANT_TRANSACTION_COMMISSION
                )

            merchant_db.amount_frozen -= transaction_db.amount
