from typing import Any, Literal

from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.blockchain.services.tron_service import TronService
from src.apps.wallets import schemas
from src.apps.wallets.model import WalletModel
from src.apps.wallets.repository import WalletRepository
from src.core import exceptions
from src.lib.base.service import BaseService


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
    not_found_exception_message = "Кошелки не найдены."
    conflict_exception_message = "Возник конфликт при создании кошелька."

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
        """

        logger.info("Создание кошелька: {}", data.model_dump())

        if not await TronService.does_wallet_exist(data.address):
            raise exceptions.BadRequestException("Кошелек не существует на блокчейне.")

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
        """

        logger.info("Получение кошелька по адресу: {}", address)

        wallet = await cls.repository.get_one_or_none(
            session, WalletModel.address == address
        )

        if not wallet:
            raise exceptions.NotFoundException("Кошелек не найден.")

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
