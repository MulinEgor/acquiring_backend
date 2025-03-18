"""Модуль для сервиса пользователей."""

from sanic import exceptions
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import src.users.schemas as schemas
from src.base.service import BaseService
from src.permissions.service import PermissionService
from src.services.hash_service import HashService
from src.services.random_service import RandomService
from src.users.models import UserModel
from src.users.repository import UserRepository
from src.users_permissions.service import UsersPermissionsService


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

        # Проверка существования разрешений
        if not await PermissionService.check_all_exist(
            session=session,
            ids=data.permissions_ids,
        ):
            raise exceptions.NotFoundException(
                message="Какие то разрешения не найдены.",
            )

        # Генерация и хэширование пароля
        password = RandomService.generate_str()
        hashed_password = HashService.generate(password)

        db_data = schemas.UserCreateRepositorySchema(
            email=data.email,
            hashed_password=hashed_password,
        )

        try:
            # Добавление пользователя в БД
            user = await cls.repository.create(
                session=session,
                obj_in=db_data,
            )

            # Добавление разрешений пользователю
            await UsersPermissionsService.add_permissions_to_user(
                session=session,
                user_id=user.id,
                permission_ids=data.permissions_ids,
            )

            await session.commit()
            await session.refresh(user)

        except IntegrityError as ex:
            raise exceptions.ConflictException(exc=ex)

        return schemas.UserCreatedGetSchema(
            **schemas.UserGetSchema.model_validate(user).model_dump(),
            password=password,
        )

    # MARK: Update
    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        user_id: int,
        data: schemas.UserUpdateSchema,
    ) -> schemas.UserGetSchema:
        """
        Обновить данные пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (int): ID пользователя.
            data (UserUpdateSchema): Данные для обновления пользователя.

        Returns:
            UserGetSchema: Обновленный пользователь.

        Raises:
            NotFoundException: Пользователь не найден.
            ConflictException: Пользователь с такими данными уже существует.
        """

        # Поиск пользователя в БД
        user = await cls.get_by_id(session, user_id)

        # Проверка существования разрешений
        if data.permissions_ids and not await PermissionService.check_all_exist(
            session=session,
            ids=data.permissions_ids,
        ):
            raise exceptions.NotFoundException(
                message="Какие то разрешения не найдены.",
            )

        hashed_password = None
        if data.password:
            hashed_password = HashService.generate(data.password)

        # Обновление пользователя в БД
        try:
            updated_user = await UserRepository.update(
                UserModel.id == user_id,
                session=session,
                obj_in=schemas.UserUpdateRepositorySchema(
                    email=data.email,
                    hashed_password=hashed_password,
                    is_active=data.is_active
                    if data.is_active is not None
                    else user.is_active,
                ),
            )

            # Обновление разрешений пользователя
            if data.permissions_ids:
                updated_user.permissions = await PermissionService.get_all_by_ids(
                    session=session,
                    ids=data.permissions_ids,
                )

            await session.commit()
            await session.refresh(updated_user)

        except IntegrityError as ex:
            raise exceptions.ConflictException(exc=ex)

        return schemas.UserGetSchema.model_validate(updated_user)
