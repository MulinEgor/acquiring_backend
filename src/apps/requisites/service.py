from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.requisites import schemas
from src.apps.requisites.model import RequisiteModel
from src.apps.requisites.repository import RequisiteRepository
from src.apps.users.model import UserModel
from src.core import exceptions
from src.lib.base.service import BaseService


class RequisiteService(
    BaseService[
        RequisiteModel,
        schemas.RequisiteCreateAdminSchema,
        schemas.RequisiteGetSchema,
        schemas.RequisitePaginationAdminSchema | schemas.RequisitePaginationSchema,
        schemas.RequisiteListGetSchema,
        schemas.RequisiteUpdateAdminSchema | schemas.RequisiteUpdateSchema,
    ],
):
    """Сервис для работы с реквизитами."""

    repository = RequisiteRepository

    # MARK: Get
    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        id: int,
        user: UserModel | None = None,
    ) -> schemas.RequisiteGetSchema:
        """
        Получить реквизиты по ID.
        Если пользователь не является администратором, то проверяется,
        является ли пользователь владельцем реквизитов.

        Args:
            session (AsyncSession): Сессия для работы с БД.
            id (int): ID реквизитов.
            user (UserModel | None): Пользователь.

        Returns:
            schemas.RequisiteGetSchema: Реквизиты.

        Raises:
            NotFoundException: Если реквизиты не найдены.
        """
        requisite = await super().get_by_id(session, id)

        if user and user.id != requisite.user_id:
            raise exceptions.NotFoundException("Реквизиты не найдены")

        return requisite

    # MARK: Update
    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        id: int,
        data: schemas.RequisiteUpdateAdminSchema | schemas.RequisiteUpdateSchema,
        user: UserModel | None = None,
    ) -> schemas.RequisiteGetSchema:
        """
        Обновить реквизиты по ID.
        Если пользователь не является администратором, то проверяется,
        является ли пользователь владельцем реквизитов.

        Args:
            session (AsyncSession): Сессия для работы с БД.
            id (int): ID реквизитов.
            data (schemas.RequisiteUpdateAdminSchema): Данные для обновления.
            user (UserModel | None): Пользователь.

        Returns:
            schemas.RequisiteGetSchema: Реквизиты.

        Raises:
            NotFoundException: Если реквизиты не найдены.
            ConflictException: Конфликт при обновлении.
        """
        requisite = await super().get_by_id(session, id)

        if user and user.id != requisite.user_id:
            raise exceptions.NotFoundException("Реквизиты не найдены")

        return await super().update(session, id, data)

    # MARK: Delete
    @classmethod
    async def delete(
        cls,
        session: AsyncSession,
        id: int,
        user: UserModel | None = None,
    ) -> None:
        """
        Удалить реквизиты по ID.
        Если пользователь не является администратором, то проверяется,
        является ли пользователь владельцем реквизитов.

        Args:
            session (AsyncSession): Сессия для работы с БД.
            id (int): ID реквизитов.
            user (UserModel | None): Пользователь.

        Raises:
            NotFoundException: Если реквизиты не найдены.
        """
        requisite = await super().get_by_id(session, id)

        if user and user.id != requisite.user_id:
            raise exceptions.NotFoundException("Реквизиты не найдены")

        await super().delete(session, id)
