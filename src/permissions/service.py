"""Модулья для сервисов для работы с разрешениями."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.base.service import BaseService
from src.permissions import schemas
from src.permissions.models import PermissionModel
from src.permissions.repository import PermissionRepository


class PermissionService(
    BaseService[
        PermissionModel,
        schemas.PermissionCreateSchema,
        schemas.PermissionGetSchema,
        schemas.PermissionPaginationSchema,
        schemas.PermissionListGetSchema,
        schemas.PermissionCreateSchema,
    ],
):
    """Сервис для работы с разрешениями."""

    repository = PermissionRepository

    @classmethod
    async def check_all_exist(
        cls,
        session: AsyncSession,
        ids: list[int],
    ) -> bool:
        """
        Проверить, существуют ли все разрешения в БД.

        Args:
            session (AsyncSession): Сессия для работы с БД.
            ids (list[int]): Список ID разрешений.

        Returns:
            bool: True, если все разрешения существуют, False в противном случае.
        """

        stmt = select(PermissionModel.id).where(PermissionModel.id.in_(ids))
        count = await cls.repository.count_subquery(session, stmt)

        return count == len(ids)

    @classmethod
    async def get_all_by_ids(
        cls,
        session: AsyncSession,
        ids: list[int],
    ) -> list[PermissionModel]:
        """
        Получить все разрешения по их ID.

        Args:
            session (AsyncSession): Сессия для работы с БД.
            ids (list[int]): Список ID разрешений.

        Returns:
            list[PermissionModel]: Список разрешений.
        """

        permissions = await cls.repository.get_all_with_pagination_from_stmt(
            session=session,
            stmt=select(PermissionModel).where(PermissionModel.id.in_(ids)),
        )

        return permissions
