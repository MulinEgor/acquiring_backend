from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.permissions import schemas
from src.apps.permissions.model import PermissionModel
from src.apps.permissions.repository import PermissionRepository
from src.libs.base.service import BaseService


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
    not_found_exception_message = "Разрешения не найдены."
    conflict_exception_message = "Возник конфликт при создании разрешения."

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
