"""Модуль для работы с авторизацией пользователей"""

from sqlalchemy.ext.asyncio import AsyncSession

import src.auth.schemas as auth_schemas
import src.users.schemas as user_schemas
from src import exceptions, utils
from src.auth.services.jwt_service import JWTService
from src.users import UserRepository, UserService


class AuthService:
    """Сервис для работы с авторизацией пользователей"""

    # MARK: Register
    @classmethod
    async def register(
        cls,
        session: AsyncSession,
        schema: user_schemas.UserCreateSchema,
    ) -> auth_schemas.JWTGetSchema:
        """
        Зарегистрировать нового пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            schema (UserCreateSchema): данные для создания пользователя.

        Returns:
            JWTGetSchema: access и refresh токены пользователя.

        Raises:
            UserAlreadyExistsException: Пользователь с такими данными уже существует.
        """

        # Создание пользователя
        user = await UserService.create(session, schema)

        # Создание токенов
        tokens = await JWTService.create_tokens(user_id=user.id)

        return tokens

    # MARK: Login
    @classmethod
    async def login(
        cls,
        session: AsyncSession,
        schema: user_schemas.UserLoginSchema,
    ) -> auth_schemas.JWTGetSchema:
        """
        Авторизовать пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            schema (UserLoginSchema): данные для авторизации пользователя.

        Returns:
            JWTGetSchema: access и refresh токены пользователя.

        Raises:
            NotFoundException: Пользователь не найден.
        """

        # Хэширование пароля
        hashed_password = utils.get_hash(schema.password)

        # Поиск пользователя в БД
        user = await UserRepository.get_one_or_none(
            session=session,
            email=schema.email,
            hashed_password=hashed_password,
        )

        if user is None:
            raise exceptions.NotFoundException()

        # Создание токенов
        tokens = await JWTService.create_tokens(user_id=user.id)

        return tokens
