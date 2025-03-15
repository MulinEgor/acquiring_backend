"""Модуль для репозитория для работы с разрешениями."""

from typing import Tuple

from sqlalchemy import Select, select

from src.base.repository import BaseRepository
from src.permissions import schemas
from src.permissions.models import PermissionModel


class PermissionRepository(
    BaseRepository[
        PermissionModel,
        schemas.PermissionCreateSchema,
        schemas.PermissionCreateSchema,
    ],
):
    """Репозиторий для работы с разрешениями."""

    model = PermissionModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.PermissionPaginationSchema,
    ) -> Select[Tuple[PermissionModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка разрешений.

        Args:
            query_params (PermissionPaginationSchema): параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(PermissionModel)

        # Фильтрация по имени разрешения с использованием ilike.
        if query_params.name:
            stmt = stmt.where(PermissionModel.name.ilike(f"%{query_params.name}%"))

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(PermissionModel.created_at.desc())
        else:
            stmt = stmt.order_by(PermissionModel.created_at)

        return stmt
