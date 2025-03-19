"""Модулья для сервисов трейдеров."""

from typing import Literal

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import exceptions
from src.modules.blockchain import schemas as blockchain_schemas
from src.modules.blockchain.models import StatusEnum, TypeEnum
from src.modules.blockchain.services import (
    BlockchainTransactionService,
    TronService,
)
from src.modules.traders import schemas
from src.modules.users import UserModel
from src.modules.wallets import WalletPaginationSchema, WalletService


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
                type=TypeEnum.PAY_IN,
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
                type=TypeEnum.PAY_IN,
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
            type=TypeEnum.PAY_IN,
        )

        # Получение транзакции по хэшу с блокчейна
        try:
            transaction = await TronService.get_transaction_by_hash(transaction_hash)

        except exceptions.NotFoundException as e:
            await BlockchainTransactionService.update_status_by_id(
                session=session,
                id=transaction_db.id,
                status=StatusEnum.FAILED,
            )
            raise e

        # Проверить данные транзакции с блокчейна с тразнакцией из БД
        if (
            transaction_db.amount != transaction["amount"]
            or transaction_db.to_address != transaction["to_address"]
            or transaction_db.type != TypeEnum.PAY_IN
        ):
            await BlockchainTransactionService.update_status_by_id(
                session=session,
                id=transaction_db.id,
                status=StatusEnum.FAILED,
            )
            raise exceptions.ConflictException("Транзакция не соответствует ожидаемой.")

        # Обновление статуса транзакции в БД на успешный
        await BlockchainTransactionService.update(
            session=session,
            id=transaction_db.id,
            data=blockchain_schemas.TransactionUpdateSchema(
                hash=transaction_hash,
                from_address=transaction["from_address"],
                status=StatusEnum.CONFIRMED,
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
                type=TypeEnum.PAY_OUT,
            )

            raise exceptions.ConflictException(
                "У вас уже есть транзакция в процессе обработки."
            )

        except exceptions.NotFoundException:
            pass

        # Проверка баланса
        if user.balance < data.amount:
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
                type=TypeEnum.PAY_OUT,
            ),
        )

        return schemas.ResponsePayOutSchema(transaction_id=transaction_db.id)
