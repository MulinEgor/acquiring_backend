"""Модуль для сервиса пользователей."""

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import src.users.schemas as schemas
import src.utils.hash as utils
from src import exceptions
from src.base.service import BaseService
from src.roles.service import RoleService
from src.users.models import UserModel
from src.users.repository import UserRepository
from src.utils.password import PasswordGenerator


class UserService(
    BaseService[
        UserModel,
        schemas.UserCreateSchema,
        schemas.UserGetSchema,
        schemas.UsersPaginationSchema,
        schemas.UsersListGetSchema,
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
        data: schemas.UserCreateSchema,
    ) -> schemas.UserCreatedGetSchema:
        """
        Создать пользователя в БД.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            data (UserCreateSchema): Данные для создания пользователя.

        Returns:
            UserCreatedGetSchema: Добавленный пользователь.

        Raises:
            NotFoundException: Роль не найдена.
            ConflictException: Пользователь уже существует.
        """

        # Поиск роли
        try:
            role = await RoleService.get_by_name(
                session=session,
                name=data.role_name,
            )
        except exceptions.NotFoundException:
            raise exceptions.NotFoundException(
                message="Роль не найдена.",
            )

        # Генерация и хэширование пароля
        password = PasswordGenerator.generate_password()
        hashed_password = utils.get_hash(password)

        data = schemas.UserCreateRepositorySchema(
            email=data.email,
            hashed_password=hashed_password,
            role_id=role.id,
        )

        try:
            # Добавление пользователя в БД
            user = await cls.repository.create(
                session=session,
                obj_in=data,
            )

            await session.commit()

        except IntegrityError as ex:
            raise exceptions.ConflictException(exc=ex)

        return schemas.UserCreatedGetSchema(
            **user.__dict__,
            password=password,
        )

    # MARK: Update
    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        user_id: uuid.UUID,
        data: schemas.UserUpdateSchema,
    ) -> schemas.UserGetSchema:
        """
        Обновить данные пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (uuid.UUID): ID пользователя.
            data (UserUpdateSchema): Данные для обновления пользователя.

        Returns:
            UserGetSchema: Обновленный пользователь.

        Raises:
            NotFoundException: Пользователь не найден.
            ConflictException: Пользователь с такими данными уже существует.
        """

        # Поиск пользователя в БД
        user = await cls.get_by_id(session, user_id)

        # Проверка роли
        role = None
        if data.role_name:
            role = await RoleService.get_by_name(
                session=session,
                name=data.role_name,
            )

        hashed_password = None
        if data.password:
            hashed_password = utils.get_hash(data.password)

        # Обновление пользователя в БД
        try:
            updated_user = await UserRepository.update(
                UserModel.id == user_id,
                session=session,
                obj_in=schemas.UserUpdateRepositorySchema(
                    email=data.email,
                    hashed_password=hashed_password,
                    role_id=role.id if role else user.role.id,
                ),
            )
            await session.commit()

        except IntegrityError as ex:
            raise exceptions.ConflictException(exc=ex)

        return schemas.UserGetSchema.model_validate(updated_user)
