"""Зависимости эндпоинтов API."""

from typing import AsyncGenerator

import jwt
from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

import src.exceptions as exceptions
from src import constants
from src.constants import AUTH_HEADER_NAME
from src.database import SessionLocal
from src.settings import settings
from src.users import UserModel
from src.users.repository import UserRepository

oauth2_scheme = APIKeyHeader(name=AUTH_HEADER_NAME, auto_error=False)


# MARK: Database
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    AsyncGenerator экземпляра `AsyncSession`.

    Выполняет `rollback` текущей транзакции, в случае любого исключения.
    Сессия закрывается внутри контекстного менеджера автоматически.

    **Коммит транзакции должен быть выполнен явно.**
    """

    async with SessionLocal() as session:
        try:
            yield session
        except Exception as ex:
            await session.rollback()
            raise ex


# MARK: Auth
async def get_current_user(
    header_value: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> UserModel:
    """
    Вернуть текущего пользователя, если передан верный `access_token`.

    Returns:
        UserModel: модель пользователя.

    Raises:
        InvalidTokenException: Невалидный токен `HTTP_401_UNAUTHORIZED`.
        TokenExpiredException: Время действия токена истекло `HTTP_401_UNAUTHORIZED`.
        UserNotFoundException: Пользователь не найден `HTTP_404_NOT_FOUND`.
    """

    token = header_value.removeprefix("Bearer ")

    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.JWT_ACCESS_SECRET,
            algorithms=[constants.ALGORITHM],
        )
        user_id = payload.get("id")
        if not user_id:
            raise exceptions.InvalidTokenException
    except Exception as e:
        if isinstance(e, jwt.ExpiredSignatureError):
            raise exceptions.TokenExpiredException
        else:
            raise exceptions.InvalidTokenException

    user_db = await UserRepository.get_one_or_none(
        session=session,
        id=user_id,
    )

    if user_db is None:
        raise exceptions.UserNotFoundException

    return user_db


async def get_current_admin(
    user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Проверяет, является ли пользователь администратором.

    Returns:
        UserModel: модель пользователя.

    Raises:
        InvalidTokenException: Невалидный токен `HTTP_401_UNAUTHORIZED`.
        TokenExpiredException: Время действия токена истекло `HTTP_401_UNAUTHORIZED`.
        UserNotFoundException: Пользователь не найден `HTTP_404_NOT_FOUND`.
        BaseForbiddenException: Недостаточно привилегий для выполнения запроса.
    """

    if not user.is_admin:
        raise exceptions.ForbiddenException
    return user


async def get_current_user_or_none(
    header_value: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> UserModel | None:
    """
    Вернуть текущего пользователя, если передан `access_token`
    или None, если `access_token` не был передан в заголовке.
    Используется для опциональной авторизации.

    Returns:
        UserModel|None: модель пользователя или None.

    Raises:
        InvalidTokenException: Невалидный токен `HTTP_401_UNAUTHORIZED`.
        TokenExpiredException: Время действия токена истекло `HTTP_401_UNAUTHORIZED`.
        UserNotFoundException: Пользователь не найден `HTTP_404_NOT_FOUND`.
    """

    if header_value:
        return await get_current_user(
            header_value=header_value,
            session=session,
        )
