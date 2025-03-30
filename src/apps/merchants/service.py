"""Модуль для сервиса для работы с мерчантами."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.merchants import schemas
from src.apps.traders.repository import TraderRepository
from src.apps.transactions import schemas as transaction_schemas
from src.apps.transactions.model import (
    TransactionPaymentMethodEnum,
    TransactionTypeEnum,
)
from src.apps.transactions.repository import TransactionRepository
from src.apps.transactions.service import TransactionService
from src.apps.users.model import UserModel
from src.core import constants, exceptions


class MerchantService:
    """Сервис для работы с мерчантами."""

    # MARK: Pay in
    @classmethod
    async def request_pay_in(
        cls,
        session: AsyncSession,
        user: UserModel,
        schema: schemas.MerchantPayInRequestSchema,
    ) -> (
        schemas.MerchantPayInResponseCardSchema | schemas.MerchantPayInResponseSBPSchema
    ):
        """
        Запрос на пополнение баланса клиентом мерчантом.
        Поиск трейдеров с похожими и вылидными реквизитами.
        Заморозка средств трейдера.
        Создание транзакции на перевод средств.
        Возвращение ответа с реквизитами для оплаты.

        Args:
            session: Сессия базы данных.
            user: Мерчант.
            schema: Схема запроса на пополнение баланса.

        Returns:
            Схема с реквизитами для оплаты.

        Raises:
            NotFoundException: Нет трейдеров с таким методом оплаты.
            ConflictException: Уже есть транзакция в процессе обработки.
        """

        logger.info(
            "Запрос на пополнение баланса мерчанта с ID: {} \
            суммой: {}",
            user.id,
            schema.amount,
        )

        # Проверка на наличие транзакции в процессе обработки
        if await TransactionRepository.get_pending_by_user_and_requisite_id(
            session=session,
            merchant_id=user.id,
        ):
            raise exceptions.ConflictException(
                "Уже есть транзакция в процессе обработки."
            )

        # Получение трейдера и его реквизитов
        trader_db, requisite_db = (
            await TraderRepository.get_by_payment_method_and_amount(
                session=session,
                payment_method=schema.payment_method,
                amount=schema.amount,
            )
            or (None, None)
        )
        if not trader_db:
            raise exceptions.NotFoundException(
                "Трейдер с таким методом оплаты не найден"
            )

        # Заморозка средств трейдера
        trader_db.amount_frozen += schema.amount

        # Создание транзакции на перевод средств
        await TransactionService.create(
            session=session,
            data=transaction_schemas.TransactionUpdateSchema(
                merchant_id=user.id,
                trader_id=trader_db.id,
                requisite_id=requisite_db.id,
                amount=schema.amount,
                payment_method=schema.payment_method,
                type=TransactionTypeEnum.PAY_IN,
            ),
        )

        await session.commit()

        # Возвращение ответа с реквизитами для оплаты
        if schema.payment_method == TransactionPaymentMethodEnum.CARD:
            return schemas.MerchantPayInResponseCardSchema(
                recipent_full_name=requisite_db.full_name,
                card_number=requisite_db.card_number,
            )
        else:
            return schemas.MerchantPayInResponseSBPSchema(
                recipent_full_name=requisite_db.full_name,
                bank_name=requisite_db.bank_name,
                phone_number=requisite_db.phone_number,
            )

    # MARK: Pay out
    @classmethod
    async def request_pay_out(
        cls,
        session: AsyncSession,
        user: UserModel,
        schema: schemas.MerchantPayOutRequestSchema,
    ) -> None:
        """
        Запрос на вывод средств для мерчанта.

        Если есть досточное количество денег на балансе,
        то находится трейдер с похожими реквизитами и с достаточным балансом,
        замораживаются средства трейдера, создается транзакция на перевод средств.

        Args:
            session: Сессия базы данных.
            user: Мерчант.
            schema: Схема запроса на вывод средств.

        Raises:
            NotFoundException: Нет трейдеров с таким методом оплаты.
            ConflictException: Уже есть транзакция в процессе обработки.
        """

        logger.info(
            "Запрос на вывод средств для мерчанта с ID: {} \
            суммой: {}",
            user.id,
            schema.amount,
        )

        if (
            user.balance - user.amount_frozen
            < schema.amount + schema.amount * constants.MERCHANT_COMMISSION
        ):
            raise exceptions.ConflictException("На балансе недостаточно средств.")

        # Проверка на наличие транзакции в процессе обработки
        if await TransactionRepository.get_pending_by_user_and_requisite_id(
            session=session,
            merchant_id=user.id,
        ):
            raise exceptions.ConflictException(
                "Уже есть транзакция в процессе обработки."
            )

        # Получение трейдера
        trader_db, requisite_db = (
            await TraderRepository.get_by_payment_method_and_amount(
                session=session,
                payment_method=schema.payment_method,
                amount=schema.amount,
            )
            or (None, None)
        )
        if not trader_db:
            raise exceptions.NotFoundException(
                "Трейдер с таким методом оплаты не найден"
            )

        # Заморозка средств трейдера
        trader_db.amount_frozen += schema.amount

        # Создание транзакции на перевод средств
        await TransactionService.create(
            session=session,
            data=transaction_schemas.TransactionUpdateSchema(
                merchant_id=user.id,
                trader_id=trader_db.id,
                requisite_id=requisite_db.id,
                amount=schema.amount,
                payment_method=schema.payment_method,
                type=TransactionTypeEnum.PAY_OUT,
            ),
        )

        await session.commit()
