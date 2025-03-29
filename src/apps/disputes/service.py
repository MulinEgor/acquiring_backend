"""Модуль для сервисов диспутов."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.disputes import schemas
from src.apps.disputes.model import DisputeModel
from src.apps.disputes.repository import DisputeRepository
from src.apps.transactions.service import TransactionService
from src.lib.base.service import BaseService


class DisputeService(
    BaseService[
        DisputeModel,
        schemas.DisputeCreateSchema,
        schemas.DisputeGetSchema,
        schemas.DisputePaginationSchema,
        schemas.DisputeListSchema,
        schemas.DisputeUpdateSchema,
    ],
):
    """Сервис для работы с диспутами."""

    repository = DisputeRepository

    @classmethod
    async def create(
        cls, session: AsyncSession, data: schemas.DisputeCreateSchema
    ) -> schemas.DisputeGetSchema:
        """
        Создать диспут.

        Args:
            session (AsyncSession): Сессия БД.
            data (DisputeCreateSchema): Схема для создания диспута.

        Returns:
            DisputeGetSchema: Схема для получения диспута.

        Raises:
            NotFoundException: Транзакция не найдена.
            ConflictException: Конфликт при создании.
        """

        await TransactionService.get_by_id(session=session, id=data.transaction_id)

        return await super().create(session=session, data=data)
