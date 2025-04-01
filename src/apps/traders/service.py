"""Модулья для сервисов трейдеров."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.notifications import schemas as notification_schemas
from src.apps.notifications.service import NotificationService
from src.apps.transactions.model import (
    TransactionStatusEnum,
    TransactionTypeEnum,
)
from src.apps.transactions.repository import TransactionRepository
from src.apps.users.model import UserModel
from src.apps.users.repository import UserRepository
from src.core import constants, exceptions


class TraderService:
    """Сервис для работы с трейдерами."""

    # MARK: Pay in
    @classmethod
    async def confirm_merchant_pay_in(
        cls,
        session: AsyncSession,
        transaction_id: int,
        trader_db: UserModel,
    ) -> None:
        """
        Подтвердить пополнение средств клиентом,
            разморозить средства трейдера с учетом комиссии,
            пополнить баланс мерчанта с учетом комиссии,
            изменить статус транзакции на "подтвержден".

        Args:
            session: Сессия БД.
            trader_db: Трейдер, который подтверждает пополнение средств.

        Raises:
            NotFoundException: Транзакция или мерчант не найдены.
        """

        logger.info(
            "Подтверждение пополнения средств клиентом от трейдера с ID: {}",
            trader_db.id,
        )

        # Получение транзакции в процессе обработки из БД
        transaction_db = await TransactionRepository.get_one_or_none(
            session=session,
            id=transaction_id,
            type=TransactionTypeEnum.PAY_IN,
            status=TransactionStatusEnum.PENDING,
        )
        if not transaction_db:
            raise exceptions.NotFoundException(
                "Транзакция для пополнения средств не найдена"
            )

        # Разморозка средств трейдера с учетом комиссии
        trader_db.balance -= trader_db.amount_frozen
        trader_db.balance += trader_db.amount_frozen * constants.TRADER_COMMISSION
        trader_db.amount_frozen = 0

        # Пополнение баланса мерчанта с учетом комиссии
        merchant_db = await UserRepository.get_one_or_none(
            session=session,
            id=transaction_db.merchant_id,
        )
        if not merchant_db:
            raise exceptions.NotFoundException("Мерчант не найден")

        merchant_db.balance += (
            transaction_db.amount
            - transaction_db.amount * constants.MERCHANT_COMMISSION
        )
        transaction_db.status = TransactionStatusEnum.SUCCESS

        await session.commit()

        # Отправление уведомления
        await NotificationService.create(
            session=session,
            data=notification_schemas.NotificationCreateSchema(
                user_id=transaction_db.merchant_id,
                message=constants.NOTIFICATION_MESSAGE_CONFIRM_MERCHANT_PAY_IN.format(
                    amount=transaction_db.amount,
                ),
            ),
        )

    # MARK: Pay out
    @classmethod
    async def confirm_merchant_pay_out(
        cls,
        session: AsyncSession,
        transaction_id: int,
        trader_db: UserModel,
    ) -> None:
        """
        Подтвердить перевод на счет мерчанта.

        Пополнить баланс мерчанта с учетом комиссии,
        разморозить средства трейдера и снять их с баланса с учетом комиссии,
        изменить статус транзакции на "подтвержден".

        Args:
            session: Сессия БД.
            transaction_id: Идентификатор транзакции.
            trader_db: Трейдер, который подтверждает перевод на счет.

        Raises:
            NotFoundException: Транзакция или трейдер не найдены.
        """

        logger.info(
            "Подтверждение перевода на счет мерчанта с ID: {}",
            trader_db.id,
        )

        # Получение транзакции в процессе обработки из БД
        transaction_db = await TransactionRepository.get_one_or_none(
            session=session,
            id=transaction_id,
            type=TransactionTypeEnum.PAY_OUT,
            status=TransactionStatusEnum.PENDING,
        )
        if not transaction_db:
            raise exceptions.NotFoundException(
                "Транзакция для перевода на счет не найдена"
            )

        # Пополнение баланса трейдера с учетом комиссии
        trader_db.balance += (
            transaction_db.amount + transaction_db.amount * constants.TRADER_COMMISSION
        )

        # Пополнение баланса мерчанта с учетом комиссии
        merchant_db = await UserRepository.get_one_or_none(
            session=session,
            id=transaction_db.merchant_id,
        )
        if not merchant_db:
            raise exceptions.NotFoundException("Мерчант не найден")

        merchant_db.balance -= (
            transaction_db.amount
            + transaction_db.amount * constants.MERCHANT_COMMISSION
        )
        merchant_db.amount_frozen -= transaction_db.amount

        transaction_db.status = TransactionStatusEnum.SUCCESS

        await session.commit()

        # Отправление уведомления
        await NotificationService.create(
            session=session,
            data=notification_schemas.NotificationCreateSchema(
                user_id=transaction_db.merchant_id,
                message=constants.NOTIFICATION_MESSAGE_CONFIRM_MERCHANT_PAY_OUT.format(
                    amount=transaction_db.amount,
                ),
            ),
        )
