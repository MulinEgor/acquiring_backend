"""Модуль для репозитория для работы с связями ролей и разрешений."""

from typing import Tuple

from sqlalchemy import Select, select

from src.base.repository import BaseRepository
from src.roles_permissions import schemas
from src.roles_permissions.models import RolesPermissionsModel


class RolesPermissionsRepository(
    BaseRepository[
        RolesPermissionsModel,
        schemas.RolesPermissionsCreateSchema,
        schemas.RolesPermissionsCreateSchema,
    ],
):
    """Репозиторий для работы с связями ролей и разрешений."""

    model = RolesPermissionsModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.RolesPermissionsPaginationSchema,
    ) -> Select[Tuple[RolesPermissionsModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка связей ролей и разрешений.

        Args:
            query_params (RolesPermissionsPaginationSchema): параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(RolesPermissionsModel)

        # Фильтрация по ID роли.
        if query_params.role_id:
            stmt = stmt.where(RolesPermissionsModel.role_id == query_params.role_id)

        # Фильтрация по ID разрешения.
        if query_params.permission_id:
            stmt = stmt.where(
                RolesPermissionsModel.permission_id == query_params.permission_id
            )

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(RolesPermissionsModel.created_at.desc())
        else:
            stmt = stmt.order_by(RolesPermissionsModel.created_at)

        return stmt
