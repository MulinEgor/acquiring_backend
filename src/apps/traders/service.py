"""Модулья для сервисов трейдеров."""

from typing import Literal

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.blockchain import schemas as blockchain_schemas
from src.apps.blockchain.services.transaction_service import (
    BlockchainTransactionService,
)
from src.apps.blockchain.services.tron_service import TronService
from src.apps.requisites.model import RequisiteModel
from src.apps.traders import schemas
from src.apps.traders.repository import TraderRepository
from src.apps.transactions.model import (
    TransactionPaymentMethodEnum,
    TransactionStatusEnum,
    TransactionTypeEnum,
)
from src.apps.transactions.service import TransactionService
from src.apps.users.model import UserModel
from src.apps.users.repository import UserRepository
from src.apps.wallets.schemas import WalletPaginationSchema
from src.apps.wallets.service import WalletService
from src.core import constants, exceptions


class TraderService:
    """Сервис для работы с трейдерами."""

    # MARK: Utils
    @classmethod
    async def _get_wallet_address_with_min_or_max_balance(
        cls,
        session: AsyncSession,
        min_or_max: Literal["min", "max"],
        amount: int,
    ) -> str:
        """
        Получить адрес кошелька на блокчейне с наименьшим или наибольшим балансом.

        Args:
            session: Сессия базы данных.
            min_or_max: Наименьший или наибольший баланс.

        Returns:
            Адрес кошелька на блокчейне.

        Raises:
            NotFoundException: Нет кошельков, куда можно перевести средства.
        """

        wallets_addresses = [
            wallet.address
            for wallet in (
                await WalletService.get_all(session, WalletPaginationSchema())
            ).data
        ]
        if not wallets_addresses:
            raise exceptions.NotFoundException(
                "Не найдены кошельки для перевода средств."
            )

        wallets_balances = await TronService.get_wallets_balances(wallets_addresses)
        wallets_balances = dict(
            filter(lambda x: x[1] >= amount, wallets_balances.items())
        )

        if not wallets_balances:
            raise exceptions.NotFoundException(
                "Не найдены кошельки с достаточным балансом."
            )

        if min_or_max == "min":
            return min(wallets_balances.items(), key=lambda x: x[1])[0]
        else:
            return max(wallets_balances.items(), key=lambda x: x[1])[0]

    # MARK: Pay in
    @classmethod
    async def request_pay_in(
        cls, session: AsyncSession, user: UserModel, amount: int
    ) -> schemas.ResponsePayInSchema:
        """
        Получить адрес кошелька на блокчейне с наименьшим балансом,
            куда нужно перевести средства.

        Создает сущность блокчейн транзакции в БД со статусом "ожидание".

        Args:
            session: Сессия БД.
            user: Пользователь, который запрашивает перевод средств.
            amount: Сумма перевода в TRX.

        Returns:
            Схема для ответа на запрос перевода средств.

        Raises:
            NotFoundException: Нет кошельков, куда можно перевести средства.
            ConflictException: Не удалось создать транзакцию или уже есть одна.
        """

        logger.info(
            "Запрос на перевод средств для пользователя с ID: {} суммой: {}",
            user.id,
            amount,
        )

        # Проверка на наличие транзакции в процессе обработки в БД
        try:
            await BlockchainTransactionService.get_pending_by_user_id(
                session=session,
                user_id=user.id,
                type=TransactionTypeEnum.PAY_IN,
            )

            raise exceptions.ConflictException(
                "У вас уже есть транзакция в процессе обработки."
            )

        except exceptions.NotFoundException:
            pass

        # Получение адресса кошелька с минимальным балансом с блокчейна
        wallet_address = await cls._get_wallet_address_with_min_or_max_balance(
            session=session, min_or_max="min", amount=amount
        )

        # Создание транзакции в БД
        await BlockchainTransactionService.create(
            session=session,
            data=blockchain_schemas.TransactionCreateSchema(
                user_id=user.id,
                to_address=wallet_address,
                amount=amount,
                type=TransactionTypeEnum.PAY_IN,
            ),
        )

        return schemas.ResponsePayInSchema(wallet_address=wallet_address)

    @classmethod
    async def confirm_pay_in(
        cls, session: AsyncSession, user: UserModel, transaction_hash: str
    ) -> None:
        """
        Подтвердить перевод средств.

        Проверяет транзакцию по хэшу, изменяет статус транзакции в БД,
            и зачисляет средства на счет пользователя.

        Args:
            session: Сессия БД.
            user: Пользователь, который подтверждает перевод средств.
            transaction_hash: Хэш транзакции.

        Raises:
            NotFoundException: Транзакция не найдена.
            ConflictException: Не удалось обновить статус транзакции.
        """

        logger.info(
            "Подтверждение перевода средств от пользователя с ID: {} \
            транзакцией с хэшем: {}",
            user.id,
            transaction_hash,
        )

        # Получение транзакции в процессе обработки из БД
        transaction_db = await BlockchainTransactionService.get_pending_by_user_id(
            session=session,
            user_id=user.id,
            type=TransactionTypeEnum.PAY_IN,
        )

        # Получение транзакции по хэшу с блокчейна
        try:
            transaction = await TronService.get_transaction_by_hash(transaction_hash)

        except exceptions.NotFoundException as e:
            await BlockchainTransactionService.update_status_by_id(
                session=session,
                id=transaction_db.id,
                status=TransactionStatusEnum.FAILED,
            )
            raise e

        # Проверить данные транзакции с блокчейна с тразнакцией из БД
        if (
            transaction_db.amount != transaction["amount"]
            or transaction_db.to_address != transaction["to_address"]
            or transaction_db.type != TransactionTypeEnum.PAY_IN
        ):
            await BlockchainTransactionService.update_status_by_id(
                session=session,
                id=transaction_db.id,
                status=TransactionStatusEnum.FAILED,
            )
            raise exceptions.ConflictException("Транзакция не соответствует ожидаемой.")

        # Обновление статуса транзакции в БД на успешный
        await BlockchainTransactionService.update(
            session=session,
            id=transaction_db.id,
            data=blockchain_schemas.TransactionUpdateSchema(
                hash=transaction_hash,
                from_address=transaction["from_address"],
                status=TransactionStatusEnum.CONFIRMED,
                created_at=transaction["created_at"],
            ),
        )

        # Зачисление средств на счет пользователя
        user.balance += transaction_db.amount
        await session.commit()

    # MARK: Pay out
    @classmethod
    async def request_pay_out(
        cls,
        session: AsyncSession,
        user: UserModel,
        data: schemas.RequestPayOutSchema,
    ) -> schemas.ResponsePayOutSchema:
        """
        Запросить вывод средств терминалом.

        Проверяет баланс пользователя,
            создает сущность блокчейн транзакции в БД со статусом "ожидание",
            которую нужно будет подтвердить суппортом.

        Args:
            session: Сессия БД.
            user: Пользователь, который запрашивает вывод средств.
            data: Схема для запроса вывода средств терминалом.

        Returns:
            Схема с идентификатором транзакции.

        Raises:
            NotFoundException: Нет кошельков, куда можно перевести средства.
            ConflictException: Не удалось создать транзакцию или уже есть одна.
        """

        logger.info(
            "Запрос на вывод средств терминалом от пользователя с ID: {} \
            суммой: {}",
            user.id,
            data.amount,
        )

        # Проверка на наличие транзакции в процессе обработки в БД
        try:
            await BlockchainTransactionService.get_pending_by_user_id(
                session=session,
                user_id=user.id,
                type=TransactionTypeEnum.PAY_OUT,
            )

            raise exceptions.ConflictException(
                "У вас уже есть транзакция в процессе обработки."
            )

        except exceptions.NotFoundException:
            pass

        # Проверка баланса
        if user.balance - user.amount_frozen < data.amount:
            raise exceptions.BadRequestException("Недостаточно средств для вывода.")

        wallet_address = await cls._get_wallet_address_with_min_or_max_balance(
            session=session, min_or_max="max", amount=data.amount
        )

        transaction_db = await BlockchainTransactionService.create(
            session=session,
            data=blockchain_schemas.TransactionCreateSchema(
                user_id=user.id,
                to_address=data.to_address,
                from_address=wallet_address,
                amount=data.amount,
                type=TransactionTypeEnum.PAY_OUT,
            ),
        )

        return schemas.ResponsePayOutSchema(transaction_id=transaction_db.id)

    # MARK: Get trader by payment method
    @classmethod
    async def get_by_payment_method_and_amount(
        cls,
        session: AsyncSession,
        payment_method: TransactionPaymentMethodEnum,
        amount: int,
    ) -> tuple[UserModel, RequisiteModel]:
        """
        Получить трейдера по методу оплаты.

        Args:
            session: Сессия БД.
            payment_method: Метод оплаты.
            amount: Сумма транзакции.

        Returns:
            Кортеж из трейдера и его реквизитов.

        Raises:
            NotFoundException: Нет трейдеров с таким методом оплаты.
        """

        result = await TraderRepository.get_by_payment_method_and_amount(
            session=session,
            payment_method=payment_method,
            amount=amount,
        )

        if not result:
            raise exceptions.NotFoundException(
                "Трейдер с таким методом оплаты не найден"
            )

        return result

    # MARK: Confirm merchant pay in
    @classmethod
    async def confirm_merchant_pay_in(
        cls,
        session: AsyncSession,
        trader_db: UserModel,
    ) -> None:
        """
        Подтвердить пополнение средств мерчантом,
            разморозить средства трейдера с учетом комиссии,
            пополнить баланс мерчанта с учетом комиссии,
            изменить статус транзакции на "подтвержден".

        Args:
            session: Сессия БД.
            trader_db: Трейдер, который подтверждает пополнение средств.

        Raises:
            NotFoundException: Транзакция   или мерчант не найдены.
        """

        logger.info(
            "Подтверждение пополнения средств мерчантом от трейдера с ID: {}",
            trader_db.id,
        )

        # Получение транзакции в процессе обработки из БД
        transaction_db = await TransactionService.get_pending_by_user_id(
            session=session,
            user_id=trader_db.id,
            type=TransactionTypeEnum.PAY_IN,
            role="trader",
        )

        # Разморозка средств трейдера с учетом комиссии
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

        transaction_db.status = TransactionStatusEnum.CONFIRMED

        await session.commit()
