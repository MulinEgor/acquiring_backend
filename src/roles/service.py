"""Модулья для сервисов для работы с ролями."""

from sqlalchemy.ext.asyncio import AsyncSession

from src import exceptions
from src.base.service import BaseService
from src.roles import schemas
from src.roles.models import RoleModel
from src.roles.repository import RoleRepository


class RoleService(
    BaseService[
        RoleModel,
        schemas.RoleCreateSchema,
        schemas.RoleGetSchema,
        schemas.RolePaginationSchema,
        schemas.RoleListGetSchema,
        schemas.RoleCreateSchema,
    ],
):
    """Сервис для работы с ролями."""

    repository = RoleRepository

    @classmethod
    async def get_by_name(
        cls,
        session: AsyncSession,
        name: str,
    ) -> schemas.RoleGetSchema:
        """
        Получить роль по названию.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            name (str): Название роли.

        Returns:
            RoleGetSchema: Роль.
        """

        role = await cls.repository.get_one_or_none(
            session=session,
            name=name,
        )

        if role is None:
            raise exceptions.NotFoundException(
                message="Роль не найдена.",
            )

        return schemas.RoleGetSchema.model_validate(role)
