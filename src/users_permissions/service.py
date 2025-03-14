"""Модуль для сервиса с разрешениями пользователей."""

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src import exceptions
from src.users_permissions import schemas
from src.users_permissions.repository import UsersPermissionsRepository


class UsersPermissionsService:
    """Сервис для работы с разрешениями пользователей."""

    repository = UsersPermissionsRepository

    # MARK: Create
    @classmethod
    async def add_permissions_to_user(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        permission_ids: list[uuid.UUID],
    ):
        """
        Добавить разрешения пользователю, удалив все существующие.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (uuid.UUID): ID пользователя.
            permission_ids (list[uuid.UUID]): ID разрешений.
        """

        # Удалить все разрешения пользователя
        await cls.repository.delete_bulk(
            session,
            user_id,
        )

        # Добавить новые разрешения
        try:
            await cls.repository.create_bulk(
                session=session,
                data=[
                    schemas.UsersPermissionsCreateSchema(
                        user_id=user_id,
                        permission_id=permission_id,
                    )
                    for permission_id in permission_ids
                ],
            )
        except IntegrityError as e:
            raise exceptions.ConflictException(exc=e)
