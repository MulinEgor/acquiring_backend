"""Модуль для работы с авторизацией пользователей"""

import json

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

import src.modules.auth.schemas as auth_schemas
import src.modules.users.schemas as user_schemas
from src.core import constants, exceptions
from src.modules.auth.services.jwt_service import JWTService
from src.modules.services.email_service import EmailService
from src.modules.services.hash_service import HashService
from src.modules.services.random_service import RandomService
from src.modules.services.redis_service import RedisService
from src.modules.users.models import UserModel
from src.modules.users.repository import UserRepository


class AuthService:
    """Сервис для работы с авторизацией пользователей"""

    # MARK: Utils
    @classmethod
    async def _send_2fa_code(
        cls,
        user: UserModel,
        background_tasks: BackgroundTasks,
    ) -> dict[str, str]:
        """
        Обрабатывает попытку входа с 2FA.
        Генерирует код, сохраняет его в Redis и отправляет на почту.

        Args:
            user (UserModel): Модель пользователя.
            background_tasks (BackgroundTasks):
                Задачи для выполнения в фоне (передается из роута).

        Returns:
            dict[str, str]: Сообщение о включении 2FA или о том,
                что письмо с кодом подтверждения уже отправлено.

        Raises:
            InternalServerErrorException:
                Не удалось отправить письмо с кодом подтверждения на почту.
        """

        redis_key_hash = HashService.generate(f"2fa_code:{user.id}")
        # Если в Redis есть ключ, то письмо уже отправлено
        if await RedisService.get(redis_key_hash):
            return {"message": "Письмо с кодом подтверждения уже отправлено на почту."}

        # Сгенерировать код и сохранить его хэш в Redis
        code = RandomService.generate_str()
        code_hash = HashService.generate(code)
        await RedisService.set(
            redis_key_hash,
            json.dumps(
                auth_schemas.Redis2FAValueSchema(code_hash=code_hash).model_dump()
            ),
        )

        # Добавить отправку письма в фоновую задачу
        background_tasks.add_task(
            EmailService.send,
            user.email,
            constants.TWO_FACTOR_LOGIN_CONFIRM_SUBJECT,
            constants.TWO_FACTOR_LOGIN_CONFIRM_MESSAGE.format(code=code),
        )

        return {"message": "Письмо с кодом подтверждения отправлено на почту."}

    @classmethod
    async def _check_and_delete_2fa_code(
        cls,
        code: str,
        user: UserModel,
    ) -> None:
        """
        Проверяет код 2FA и удаляет его из Redis, если он верный.

        Args:
            code (str): код для подтверждения 2-х факторной авторизации.
            user (UserModel): модель пользователя.

        Raises:
            BadRequestException: Нет действующих кодов подтверждения или код неверен.
        """

        redis_key_hash = HashService.generate(f"2fa_code:{user.id}")
        raw_redis_value = await RedisService.get(redis_key_hash)

        if not raw_redis_value:
            raise exceptions.BadRequestException(
                "Нет действующих кодов подтверждения, отправьте новый код."
            )

        redis_value_schema = auth_schemas.Redis2FAValueSchema(
            **json.loads(raw_redis_value)
        )
        # Проверить количество попыток ввода кода
        if redis_value_schema.tries >= constants.TWO_FACTOR_MAX_CODE_TRIES:
            raise exceptions.BadRequestException(
                "Превышено количество попыток ввода кода."
            )

        # Если код неверный, увеличить количество попыток и вернуть ошибку
        if HashService.generate(code) != redis_value_schema.code_hash:
            redis_value_schema.tries += 1
            await RedisService.set(
                redis_key_hash,
                json.dumps(redis_value_schema.model_dump()),
            )
            raise exceptions.BadRequestException("Неверный код.")

        # Удалить код из Redis
        await RedisService.delete(redis_key_hash)

    # MARK: Login
    @classmethod
    async def login(
        cls,
        session: AsyncSession,
        background_tasks: BackgroundTasks,
        schema: user_schemas.UserLoginSchema,
    ) -> auth_schemas.JWTGetSchema | dict[str, str]:
        """
        Авторизовать пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            background_tasks (BackgroundTasks):
                Задачи для выполнения в фоне (передается из роута).
            schema (UserLoginSchema): данные для авторизации пользователя.

        Returns:
            JWTGetSchema | dict[str, str]: access и refresh токены пользователя
            или сообщение о включении 2FA.

        Raises:
            NotFoundException: Пользователь не найден.
        """

        # Хэширование пароля
        hashed_password = HashService.generate(schema.password)

        # Поиск пользователя в БД
        user = await UserRepository.get_one_or_none(
            session=session,
            email=schema.email,
            hashed_password=hashed_password,
        )

        if user is None:
            raise exceptions.NotFoundException()

        if user.is_2fa_enabled:
            return await cls._send_2fa_code(user, background_tasks)

        # Создание токенов
        tokens = await JWTService.create_tokens(user_id=user.id)

        return tokens

    @classmethod
    async def login_2fa(
        cls,
        session: AsyncSession,
        code_schema: auth_schemas.TwoFactorCodeCheckSchema,
    ) -> auth_schemas.JWTGetSchema:
        """
        Авторизовать пользователя с 2FA после ввода кода.

        Args:
            session (AsyncSession): сессия для работы с базой данных.
            code_schema (TwoFactorCodeSchema):
                схема для подтверждения 2-х факторной авторизации.

        Returns:
            JWTGetSchema: access и refresh токены пользователя.

        Raises:
            NotFoundException: Пользователь не найден.
            BadRequestException: 2FA не включена,
                нет действующих кодов подтверждения или код неверен.
        """

        user = await UserRepository.get_one_or_none(
            session=session,
            email=code_schema.email,
        )

        if user is None:
            raise exceptions.NotFoundException()

        if not user.is_2fa_enabled:
            raise exceptions.BadRequestException("2FA не включено.")

        await cls._check_and_delete_2fa_code(code_schema.code, user)

        # Создание токенов
        tokens = await JWTService.create_tokens(user_id=user.id)

        return tokens

    # MARK: Send 2FA code
    @classmethod
    async def send_2fa_code(
        cls,
        session: AsyncSession,
        background_tasks: BackgroundTasks,
        email: str,
    ) -> dict[str, str]:
        """
        Отправить код для 2FA.

        Args:
            session (AsyncSession): сессия для работы с базой данных.
            background_tasks (BackgroundTasks):
                Задачи для выполнения в фоне (передается из роута).
            email (str): email пользователя.

        Returns:
            dict[str, str]: Сообщение о включении 2FA или о том,
                что письмо с кодом подтверждения уже отправлено.
        """

        user = await UserRepository.get_one_or_none(
            session=session,
            email=email,
        )

        if user is None:
            raise exceptions.NotFoundException()

        return await cls._send_2fa_code(user, background_tasks)

    # MARK: Enable/disable 2FA
    @classmethod
    async def enable_or_disable_2fa(
        cls,
        session: AsyncSession,
        code_schema: auth_schemas.TwoFactorCodeCheckSchema,
        should_enable: bool,
    ) -> dict[str, str]:
        """
        Включить или выключить 2FA.

        Args:
            session (AsyncSession): сессия для работы с базой данных.
            code_schema (TwoFactorCodeSchema): схема для подтверждения.
            should_enable (bool): флаг для включения или выключения 2FA.

        Returns:
            dict[str, str]: Сообщение о включении или выключении 2FA.

        Raises:
            NotFoundException: Пользователь не найден.
            BadRequestException: 2FA не включено, нет действующих кодов подтверждения,
                или код неверен.
        """

        user = await UserRepository.get_one_or_none(
            session=session,
            email=code_schema.email,
        )

        if not user:
            raise exceptions.NotFoundException()

        if user.is_2fa_enabled == should_enable:
            raise exceptions.BadRequestException(
                f"2FA уже {'включено' if should_enable else 'выключено'}."
            )

        await cls._check_and_delete_2fa_code(code_schema.code, user)

        user.is_2fa_enabled = should_enable
        await session.commit()

        return {
            "message": "2FA успешно включено."
            if should_enable
            else "2FA успешно выключено."
        }
