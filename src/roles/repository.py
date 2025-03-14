"""Модуль для репозитория для работы с ролями."""

from typing import Tuple

from sqlalchemy import Select, select

from src.base.repository import BaseRepository
from src.roles import schemas
from src.roles.models import RoleModel


class RoleRepository(
    BaseRepository[
        RoleModel,
        schemas.RoleCreateSchema,
        schemas.RoleCreateSchema,
    ],
):
    """Репозиторий для работы с ролями."""

    model = RoleModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.RolePaginationSchema,
    ) -> Select[Tuple[RoleModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка ролей.

        Args:
            query_params (RolePaginationSchema): параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(RoleModel)

        # Фильтрация по имени роли с использованием ilike.
        if query_params.name:
            stmt = stmt.where(RoleModel.name.ilike(f"%{query_params.name}%"))

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(RoleModel.created_at.desc())
        else:
            stmt = stmt.order_by(RoleModel.created_at)

        return stmt
