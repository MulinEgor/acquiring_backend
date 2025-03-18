"""Модуль для работы с сервисами кошельков."""

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src import exceptions
from src.base.service import BaseService
from src.services.tron_scan_service import TronScanService
from src.wallets import schemas
from src.wallets.models import WalletModel
from src.wallets.repository import WalletRepository


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

        if not await TronScanService.does_wallet_exist(data.address):
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

        wallet = await cls.repository.get_one_or_none(
            session, WalletModel.address == address
        )

        if not wallet:
            raise exceptions.NotFoundException()

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
        await cls.get_by_address(session, address)

        await session.execute(delete(WalletModel).where(WalletModel.address == address))
        await session.commit()
