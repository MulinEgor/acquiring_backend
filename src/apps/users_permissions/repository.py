from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users_permissions import schemas
from src.apps.users_permissions.model import UsersPermissionsModel
from src.libs.base.repository import BaseRepository


class UsersPermissionsRepository(
    BaseRepository[
        UsersPermissionsModel,
        schemas.UsersPermissionsCreateSchema,
        Any,
    ],
):
    """Репозиторий для работы с разрешениями пользователей."""

    model = UsersPermissionsModel

    # MARK: Delete
    @classmethod
    async def delete_bulk(
        cls,
        session: AsyncSession,
        user_id: int,
    ):
        """
        Удалить все разрешения пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (int): ID пользователя.
        """

        await session.execute(
            delete(cls.model).filter(cls.model.user_id == user_id),
        )

        await session.commit()
