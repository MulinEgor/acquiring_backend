"""Модуль для репозитория для работы с связями ролей и разрешений."""

from typing import Tuple

from sqlalchemy import Select, select

from src.base.repository import BaseRepository
from src.roles_permissions import schemas
from src.roles_permissions.models import RolesPermissions


class RolesPermissionsRepository(
    BaseRepository[
        RolesPermissions,
        schemas.RolesPermissionsCreateSchema,
        schemas.RolesPermissionsCreateSchema,
    ],
):
    """Репозиторий для работы с связями ролей и разрешений."""

    model = RolesPermissions

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.RolesPermissionsPaginationSchema,
    ) -> Select[Tuple[RolesPermissions]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка связей ролей и разрешений.

        Args:
            query_params (RolesPermissionsPaginationSchema): параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(RolesPermissions)

        # Фильтрация по ID роли.
        if query_params.role_id:
            stmt = stmt.where(RolesPermissions.role_id == query_params.role_id)

        # Фильтрация по ID разрешения.
        if query_params.permission_id:
            stmt = stmt.where(
                RolesPermissions.permission_id == query_params.permission_id
            )

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(RolesPermissions.created_at.desc())
        else:
            stmt = stmt.order_by(RolesPermissions.created_at)

        return stmt
