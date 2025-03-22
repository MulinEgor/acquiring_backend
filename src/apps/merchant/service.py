"""Модуль для сервиса для работы с мерчантами."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.merchant import schemas
from src.apps.traders.service import TraderService
from src.apps.transactions import schemas as transaction_schemas
from src.apps.transactions.model import (
    TransactionPaymentMethodEnum,
    TransactionTypeEnum,
)
from src.apps.transactions.service import TransactionService
from src.apps.users.model import UserModel
from src.core import exceptions


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
        schemas.MerchantPayInResponseCardSchema | schemas.MerchantPayInResponseSbpSchema
    ):
        """
        Запрос на пополнение баланса мерчанта.
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
        try:
            await TransactionService.get_pending_by_user_id(
                session=session,
                user_id=user.id,
                type=TransactionTypeEnum.PAY_IN,
                role="merchant",
            )

            raise exceptions.ConflictException(
                "Уже есть транзакция в процессе обработки."
            )

        except exceptions.NotFoundException:
            pass

        # Получение трейдера и его реквизитов
        trader_db, requisite_db = await TraderService.get_by_payment_method(
            session=session,
            payment_method=schema.payment_method,
        )

        # Заморозка средств трейдера
        trader_db.amount_frozen += schema.amount

        # Создание транзакции на перевод средств
        await TransactionService.create(
            session=session,
            data=transaction_schemas.TransactionUpdateSchema(
                merchant_id=user.id,
                trader_id=trader_db.id,
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
            return schemas.MerchantPayInResponseSbpSchema(
                recipent_full_name=requisite_db.full_name,
                bank_name=requisite_db.bank_name,
                phone_number=requisite_db.phone_number,
            )
