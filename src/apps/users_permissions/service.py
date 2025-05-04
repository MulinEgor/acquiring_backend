from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.permissions.model import PermissionModel
from src.apps.users_permissions import schemas
from src.apps.users_permissions.model import UsersPermissionsModel
from src.apps.users_permissions.repository import UsersPermissionsRepository
from src.core import exceptions


class UsersPermissionsService:
    """Сервис для работы с разрешениями пользователей."""

    repository = UsersPermissionsRepository
    not_found_exception_message = "Разрешения не найдены."
    conflict_exception_message = "Возник конфликт при создании разрешения."

    # MARK: Create
    @classmethod
    async def add_permissions_to_user(
        cls,
        session: AsyncSession,
        user_id: int,
        permission_ids: list[int],
    ):
        """
        Добавить разрешения пользователю, удалив все существующие.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (int): ID пользователя.
            permission_ids (list[int]): ID разрешений.
        """

        logger.info(
            "Добавление разрешений пользователю с ID: {} \
             разрешениями: {}",
            user_id,
            permission_ids,
        )

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
            raise exceptions.ConflictException(
                message=cls.conflict_exception_message, exc=e
            )

    # MARK: Get
    @classmethod
    async def get_user_permissions(
        cls,
        session: AsyncSession,
        user_id: int,
    ) -> list[PermissionModel]:
        """
        Получить разрешения пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (int): ID пользователя.

        Returns:
            list[PermissionModel]: Список разрешений.
        """

        logger.info("Получение разрешений для пользователя с ID: {}", user_id)

        user_permissions = await cls.repository.get_all_with_pagination_from_stmt(
            session,
            stmt=select(UsersPermissionsModel).where(
                UsersPermissionsModel.user_id == user_id,
            ),
        )

        return [permission.permission for permission in user_permissions]
