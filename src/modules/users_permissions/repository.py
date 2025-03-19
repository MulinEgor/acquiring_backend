"""Модуль для репозитория с разрешениями пользователей."""

import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.base import BaseRepository
from src.modules.users_permissions import schemas
from src.modules.users_permissions.models import UsersPermissionsModel


class UsersPermissionsRepository(
    BaseRepository[
        UsersPermissionsModel,
        schemas.UsersPermissionsCreateSchema,
        any,
    ],
):
    """Репозиторий для работы с разрешениями пользователей."""

    model = UsersPermissionsModel

    # MARK: Delete
    @classmethod
    async def delete_bulk(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
    ):
        """
        Удалить все разрешения пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (uuid.UUID): ID пользователя.
        """

        await session.execute(
            delete(cls.model).filter(cls.model.user_id == user_id),
        )

        await session.commit()
