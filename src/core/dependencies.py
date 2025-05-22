from typing import AsyncGenerator

import jwt
from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

import src.apps.auth.exceptions as auth_exceptions
from src.apps.users.model import UserModel
from src.apps.users.repository import UserRepository
from src.apps.users_permissions.service import UsersPermissionsService
from src.core import constants, exceptions
from src.core.database import SessionLocal
from src.core.settings import settings

oauth2_scheme = APIKeyHeader(name=constants.AUTH_HEADER_NAME, auto_error=False)


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
            raise auth_exceptions.InvalidTokenException()
    except Exception as e:
        if isinstance(e, jwt.ExpiredSignatureError):
            raise auth_exceptions.TokenExpiredException()
        else:
            raise auth_exceptions.InvalidTokenException()

    user_db = await UserRepository.get_one_or_none(
        session=session,
        id=user_id,
    )

    if user_db is None:
        raise exceptions.NotFoundException()

    return user_db


def check_user_permissions(
    permissions: list[constants.PermissionEnum],
):
    """
    Декоратор для проверки наличия разрешений у пользователя.

    Args:
        permissions: Список разрешений.

    Raises:
        NotAuthorizedException: Пользователь не авторизован.
        ForbiddenException: Пользователь не имеет необходимых разрешений.
    """

    async def wrapper(
        user: UserModel | None = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> None:
        if not user:
            raise auth_exceptions.NotAuthorizedException()

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
