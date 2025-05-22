from typing import Any, Literal

from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.blockchain.services.tron_service import TronService
from src.apps.wallets import constants, schemas
from src.apps.wallets.model import WalletModel
from src.apps.wallets.repository import WalletRepository
from src.core import exceptions
from src.libs.base.service import BaseService


class WalletService(
    BaseService[
        WalletModel,
        schemas.WalletCreateSchema,
        schemas.WalletGetSchema,
        schemas.WalletPaginationSchema,
        schemas.WalletListSchema,
        Any,
    ],
):
    """Сервис для работы с кошельками."""

    repository = WalletRepository
    not_found_exception_message, not_found_exception_code = (
        constants.NOT_FOUND_EXCEPTION_MESSAGE,
        constants.NOT_FOUND_EXCEPTION_CODE,
    )
    conflict_exception_message, conflict_exception_code = (
        constants.CONFLICT_EXCEPTION_MESSAGE,
        constants.CONFLICT_EXCEPTION_CODE,
    )

    # MARK: Create
    @classmethod
    async def create(
        cls, session: AsyncSession, data: schemas.WalletCreateSchema
    ) -> schemas.WalletGetSchema:
        """
        Создать кошелек.
        Проверяет существование кошелька на блокчейне.

        Args:
            session: Сессия базы данных.
            data: Данные для создания кошелька.

        Returns: Кошелек.

        Raises:
            NotFoundException: Кошелек не существует на блокчейне.
        """

        logger.info("Создание кошелька: {}", data.model_dump())

        if not await TronService.does_wallet_exist(data.address):
            raise exceptions.NotFoundException(
                message=cls.not_found_exception_message,
                code=cls.not_found_exception_code,
            )

        return await super().create(session, data)

    # MARK: Get
    @classmethod
    async def get_by_address(
        cls, session: AsyncSession, address: str
    ) -> schemas.WalletGetSchema:
        """
        Получить кошелек по адресу.

        Args:
            session: Сессия базы данных.
            address: Адрес кошелька.

        Returns: Кошелек.

        Raises:
            NotFoundException: Кошелек не найден.
        """

        logger.info("Получение кошелька по адресу: {}", address)

        wallet = await cls.repository.get_one_or_none(
            session, WalletModel.address == address
        )

        if not wallet:
            raise exceptions.NotFoundException(
                message=cls.not_found_exception_message,
                code=cls.not_found_exception_code,
            )

        return schemas.WalletGetSchema.model_validate(wallet)

    @classmethod
    async def get_wallet_address_with_min_or_max_balance(
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
                await cls.get_all(session, schemas.WalletPaginationSchema())
            ).data
        ]
        if not wallets_addresses:
            raise exceptions.NotFoundException(
                message=cls.not_found_exception_message,
                code=cls.not_found_exception_code,
            )

        wallets_balances = await TronService.get_wallets_balances(wallets_addresses)
        wallets_balances = dict(
            filter(lambda x: x[1] >= amount, wallets_balances.items())
        )

        if not wallets_balances:
            raise exceptions.NotFoundException(
                message=cls.not_found_exception_message,
                code=cls.not_found_exception_code,
            )

        if min_or_max == "min":
            return min(wallets_balances.items(), key=lambda x: x[1])[0]
        else:
            return max(wallets_balances.items(), key=lambda x: x[1])[0]

    # MARK: Delete
    @classmethod
    async def delete_by_address(cls, session: AsyncSession, address: str) -> None:
        """
        Удалить кошелек по адресу.

        Args:
            session: Сессия базы данных.
            address: Адрес кошелька.

        Raises:
            NotFoundException: Кошелек не найден.
        """

        logger.info("Удаление кошелька по адресу: {}", address)

        await cls.get_by_address(session, address)

        await session.execute(delete(WalletModel).where(WalletModel.address == address))
        await session.commit()
