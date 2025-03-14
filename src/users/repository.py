"""Модуль для репозиториев пользователей."""

from typing import Tuple

from sqlalchemy import Select, select

import src.users.schemas as schemas
from src.base.repository import BaseRepository
from src.users.models import UserModel


class UserRepository(
    BaseRepository[
        UserModel,
        schemas.UserCreateSchema,
        schemas.UserUpdateSchema,
    ],
):
    """
    Основной репозиторий для работы с моделью UserModel.
    Наследуется от базового репозитория.
    """

    model = UserModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.UsersPaginationSchema,
    ) -> Select[Tuple[UserModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка пользователей.

        Args:
            query_params (UsersPaginationSchema): параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(UserModel)

        # Фильтрация по строковым полям.
        if query_params.email:
            stmt = stmt.where(UserModel.email.ilike(f"%{query_params.email}%"))

        if query_params.permissions_ids:
            raise NotImplementedError("Фильтрация по разрешениям не реализована.")

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(UserModel.created_at.desc())
        else:
            stmt = stmt.order_by(UserModel.created_at)

        return stmt
