"""Модуль для сервиса для работы с связями ролей и разрешений."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src import exceptions
from src.base.service import BaseService
from src.roles_permissions import schemas
from src.roles_permissions.models import RolesPermissions
from src.roles_permissions.repository import RolesPermissionsRepository


class RolesPermissionsService(
    BaseService[
        RolesPermissions,
        schemas.RolesPermissionsCreateSchema,
        schemas.RolesPermissionsGetSchema,
        schemas.RolesPermissionsPaginationSchema,
        schemas.RolesPermissionsListGetSchema,
        schemas.RolesPermissionsCreateSchema,
    ],
):
    """Сервис для работы с связями ролей и разрешений."""

    repository = RolesPermissionsRepository

    @classmethod
    async def get_by_role_and_permission_ids(
        cls,
        session: AsyncSession,
        role_id: uuid.UUID,
        permission_id: uuid.UUID,
    ) -> schemas.RolesPermissionsGetSchema:
        """Получить связь роли и разрешения по ID роли и ID разрешения."""

        role_permission = await cls.repository.get_one_or_none(
            session,
            RolesPermissions.role_id == role_id,
            RolesPermissions.permission_id == permission_id,
        )

        if not role_permission:
            raise exceptions.NotFoundException()

        return schemas.RolesPermissionsGetSchema(
            role=schemas.RoleGetSchema.model_validate(role_permission.role),
            permission=schemas.PermissionGetSchema.model_validate(
                role_permission.permission
            ),
            created_at=role_permission.created_at,
            updated_at=role_permission.updated_at,
        )

    # MARK: Delete
    @classmethod
    async def delete_by_role_and_permission_ids(
        cls,
        session: AsyncSession,
        role_id: uuid.UUID,
        permission_id: uuid.UUID,
    ):
        """
        Удалить связь роли и разрешения по ID роли и ID разрешения.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            role_id (uuid.UUID): ID роли.
            permission_id (uuid.UUID): ID разрешения.

        Raises:
            NotFoundException: Объект не найден.
        """

        # Поиск объекта в БД
        await cls.get_by_role_and_permission_ids(
            session=session,
            role_id=role_id,
            permission_id=permission_id,
        )

        # Удаление объекта из БД
        await cls.repository.delete(
            session=session,
            role_id=role_id,
            permission_id=permission_id,
        )
        await session.commit()
