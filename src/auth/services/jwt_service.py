"""Модуль для сервисов JWT."""

from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from sqlalchemy.ext.asyncio import AsyncSession

import src.auth.schemas as schemas
from src import constants, exceptions
from src.settings import settings
from src.users import UserRepository


class JWTService:
    """Сервис для работы с JWT."""

    # MARK: Utils
    @classmethod
    async def _decode_refresh_token(cls, refresh_token: str) -> str:
        """
        Декодировать refresh_token.

        Args:
            refresh_token (str): refresh_token.

        Returns:
            user_id: id пользователя

        Raises:
            InvalidTokenException: Невалидный токен `HTTP_401_UNAUTHORIZED`.
            TokenExpiredException: Время действия токена истекло
                `HTTP_401_UNAUTHORIZED`.
        """

        try:
            payload = jwt.decode(
                jwt=refresh_token,
                key=settings.JWT_REFRESH_SECRET,
                algorithms=[constants.ALGORITHM],
            )
            user_id = payload.get("id")

            if not user_id:
                raise exceptions.InvalidTokenException()

            return user_id
        except Exception as e:
            if isinstance(e, jwt.ExpiredSignatureError):
                raise exceptions.TokenExpiredException()
            else:
                raise exceptions.InvalidTokenException()

    # MARK: Create
    @classmethod
    async def _create_token(
        cls,
        user_id: str,
        token_type: Literal["access_token", "refresh_token"],
    ) -> tuple[str, datetime]:
        """
        Создать access_token или refresh_token для пользователя.

        Args:
            user_id(str): id пользователя.
            token_type(Literal["access_token", "refresh_token"]):
                access_token или refresh_token.

        Returns:
            (token, expires_at): токен в формате `Bearer <token>` и время его истечения.
        """

        if token_type == "access_token":
            expires_delta = settings.JWT_ACCESS_EXPIRE_MINUTES
            secret_key = settings.JWT_ACCESS_SECRET
        else:
            expires_delta = settings.JWT_REFRESH_EXPIRE_MINUTES
            secret_key = settings.JWT_REFRESH_SECRET

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)

        encoded_jwt = jwt.encode(
            payload={
                "id": str(user_id),
                "exp": expires_at,
            },
            key=secret_key,
            algorithm=constants.ALGORITHM,
        )

        return f"Bearer {encoded_jwt}", expires_at

    @classmethod
    async def create_tokens(cls, user_id: str) -> schemas.JWTGetSchema:
        """
        Метод для создания access и refresh токенов.

        Args:
            user_id (str): id пользователя.

        Returns:
            schemas.JWTGetSchema: Схема с access и refresh токенами.
        """

        access_token, expires_at = await cls._create_token(
            user_id=user_id,
            token_type="access_token",
        )
        refresh_token, _ = await cls._create_token(
            user_id=user_id,
            token_type="refresh_token",
        )

        return schemas.JWTGetSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )

    # MARK: Refresh
    @classmethod
    async def refresh_tokens(
        cls,
        session: AsyncSession,
        tokens_data: schemas.JWTRefreshSchema,
    ) -> schemas.JWTGetSchema:
        """
        Метод для обновления access и refresh токенов.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            tokens_data (JWTRefreshSchema): Схема с refresh токеном.

        Returns:
            schemas.JWTGetSchema: Схема с access и refresh токенами.

        Raises:
            InvalidTokenException: Невалидный токен `HTTP_401_UNAUTHORIZED`.
            TokenExpiredException: Время действия токена истекло
                `HTTP_401_UNAUTHORIZED`.
            NotFoundException: Пользователь не найден.
        """

        refresh_token = tokens_data.refresh_token.removeprefix("Bearer ")

        user_id = await cls._decode_refresh_token(refresh_token=refresh_token)

        user_db = await UserRepository.get_one_or_none(
            session=session,
            id=user_id,
        )

        if user_db is None:
            raise exceptions.NotFoundException()

        return await cls.create_tokens(user_id=user_id)
