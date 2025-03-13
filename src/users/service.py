"""Модуль для сервиса пользователей."""

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import src.users.schemas as schemas
from src import exceptions, utils
from src.base import BaseService
from src.users.models import UserModel
from src.users.repository import UserRepository


class UserService(
    BaseService[
        UserModel,
        schemas.UserCreateSchema,
        schemas.UserGetAdminSchema,
        schemas.UsersQuerySchema,
        schemas.UserListGetSchema,
        schemas.UserUpdateSchema,
    ],
):
    """Сервис для работы с пользователями."""

    repository = UserRepository

    # MARK: Create
    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: schemas.UserCreateSchema | schemas.UserCreateAdminSchema,
    ) -> schemas.UserGetAdminSchema:
        """
        Создать пользователя в БД.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            data (UserCreateSchema | UserCreateAdminSchema):
                Данные для создания пользователя.

        Returns:
            UserReadAdminSchema: Добавленный пользователь.

        Raises:
            ConflictException: Пользователь уже существует.
        """

        try:
            # Хэширование пароля
            hashed_password = utils.get_hash(data.password)
            data = schemas.UserCreateRepositorySchema(
                email=data.email,
                hashed_password=hashed_password,
            )

            # Добавление пользователя в БД
            user = await cls.repository.create(
                session=session,
                obj_in=data,
            )
            await session.commit()
            return schemas.UserGetAdminSchema.model_validate(user)

        except IntegrityError as ex:
            raise exceptions.ConflictException(exc=ex)

    # MARK: Update
    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        data: schemas.UserUpdateSchema | schemas.UserUpdateAdminSchema,
    ) -> schemas.UserGetAdminSchema:
        """
        Обновить данные пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (uuid.UUID): ID пользователя.
            data (UserUpdateSchema | UserUpdateAdminSchema):
                Данные для обновления пользователя.

        Returns:
            UserReadAdminSchema: Обновленный пользователь.

        Raises:
            NotFoundException: Пользователь не найден.
            ConflictException: Пользователь с такими данными уже существует.
        """

        # Поиск пользователя в БД
        await cls.get_by_id(session, user_id)

        hashed_password = None
        if data.password:
            hashed_password = utils.get_hash(data.password)

        # Обновление пользователя в БД
        try:
            updated_user = await UserRepository.update(
                UserModel.id == user_id,
                session=session,
                obj_in=schemas.UserUpdateRepositoryAdminSchema(
                    email=data.email,
                    hashed_password=hashed_password,
                    is_admin=data.is_admin
                    if isinstance(data, schemas.UserUpdateAdminSchema)
                    else None,
                ),
            )
            await session.commit()

        except IntegrityError as ex:
            raise exceptions.ConflictException(exc=ex)

        return schemas.UserGetAdminSchema.model_validate(updated_user)
