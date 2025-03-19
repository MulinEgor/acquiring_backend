"""Модуль для работы с сервисами кошельков."""

from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import exceptions
from src.core.base.service import BaseService
from src.modules.blockchain.services.tron_service import TronService
from src.modules.wallets import schemas
from src.modules.wallets.models import WalletModel
from src.modules.wallets.repository import WalletRepository


class WalletService(
    BaseService[
        WalletModel,
        schemas.WalletCreateSchema,
        schemas.WalletGetSchema,
        schemas.WalletPaginationSchema,
        schemas.WalletListSchema,
        any,
    ],
):
    """Сервис для работы с кошельками."""

    repository = WalletRepository

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

        logger.info("Создание кошелька: {}", data)

        if not await TronService.does_wallet_exist(data.address):
            logger.warning("Кошелек не существует на блокчейне: {}", data.address)
            raise exceptions.BadRequestException("Кошелек не существует на блокчейне.")

        return await super().create(session, data)

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
            logger.warning("Кошелек с адресом: {} не найден", address)
            raise exceptions.NotFoundException("Кошелек не найден.")

        logger.success("Кошелек с адресом: {} найден", address)

        return schemas.WalletGetSchema.model_validate(wallet)

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

        logger.success("Кошелек с адресом: {} удален", address)
