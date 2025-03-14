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
from src.permissions.enums import PermissionEnum
from src.settings import settings
from src.users.models import UserModel
from src.users.repository import UserRepository
from src.users_permissions.service import UsersPermissionsService

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
async def get_current_user_or_none(
    header_value: str | None = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> UserModel | None:
    """
    Вернуть текущего пользователя, если передан верный `access_token`.

    Returns:
        UserModel | None: модель пользователя.

    Raises:
        InvalidTokenException: Невалидный токен `HTTP_401_UNAUTHORIZED`.
        TokenExpiredException: Время действия токена истекло `HTTP_401_UNAUTHORIZED`.
        NotFoundException: Пользователь не найден `HTTP_404_NOT_FOUND`.
        ForbiddenException: Пользователь заблокирован `HTTP_403_FORBIDDEN`.
    """

    if not header_value:
        return None

    token = header_value.removeprefix("Bearer ")

    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.JWT_ACCESS_SECRET,
            algorithms=[constants.ALGORITHM],
        )
        user_id = payload.get("id")
        if not user_id:
            raise exceptions.InvalidTokenException()
    except Exception as e:
        if isinstance(e, jwt.ExpiredSignatureError):
            raise exceptions.TokenExpiredException()
        else:
            raise exceptions.InvalidTokenException()

    user_db = await UserRepository.get_one_or_none(
        session=session,
        id=user_id,
    )

    if user_db is None:
        raise exceptions.NotFoundException()

    if not user_db.is_active:
        raise exceptions.ForbiddenException("Ваш аккаунт заблокирован.")

    return user_db


def check_user_permissions(
    permissions: list[PermissionEnum],
):
    """
    Декоратор для проверки наличия разрешений у пользователя.

    Args:
        permissions: Список разрешений.

    Raises:
        ForbiddenException: Пользователь не имеет необходимых разрешений.
    """

    async def wrapper(
        user: UserModel | None = Depends(get_current_user_or_none),
        session: AsyncSession = Depends(get_session),
    ):
        if not user:
            raise exceptions.ForbiddenException()

        user_permissions = await UsersPermissionsService.get_user_permissions(
            session,
            user.id,
        )
        user_permissions_names = {permission.name for permission in user_permissions}

        if not set([permission.value for permission in permissions]).issubset(
            user_permissions_names
        ):
            raise exceptions.ForbiddenException()

    return wrapper
