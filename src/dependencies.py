"""Зависимости эндпоинтов API."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import jwt
import sanic
from sanic import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src import constants, exceptions
from src.database import SessionLocal
from src.settings import settings
from src.users.models import UserModel
from src.users.repository import UserRepository


# MARK: Database
@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Получить сессию для работы с базой данных.

    Выполнить `rollback` текущей транзакции, в случае любого исключения.
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
async def get_current_user(request: Request) -> UserModel:
    """
    Вернуть текущего пользователя, если передан верный `access_token`.

    Returns:
        UserModel: модель пользователя.

    Raises:
        InvalidToken: Невалидный токен `HTTP_401_UNAUTHORIZED`.
        TokenExpired: Время действия токена истекло `HTTP_401_UNAUTHORIZED`.
        NotFound: Пользователь не найден `HTTP_404_NOT_FOUND`.
        Forbidden: Пользователь заблокирован `HTTP_403_FORBIDDEN`.
    """
    raw_token = request.headers.get(constants.AUTH_HEADER_NAME)

    if not raw_token:
        raise sanic.exceptions.Unauthorized()

    token = raw_token.removeprefix("Bearer ")

    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.JWT_ACCESS_SECRET,
            algorithms=[constants.ALGORITHM],
        )
        user_id = payload.get("id")
        if not user_id:
            raise sanic.exceptions.Unauthorized()

    except Exception as e:
        if isinstance(e, jwt.ExpiredSignatureError):
            raise exceptions.TokenExpired()
        else:
            raise exceptions.InvalidToken()

    async with request.app.ctx.get_db_session() as session:
        user_db = await UserRepository.get_one_or_none(
            session=session,
            id=user_id,
        )

    if user_db is None:
        raise sanic.exceptions.NotFound()

    if not user_db.is_active:
        raise sanic.exceptions.Forbidden("Ваш аккаунт заблокирован.")

    return user_db


# def check_user_permissions(
#     permissions: list[PermissionEnum],
# ):
#     """
#     Декоратор для проверки наличия разрешений у пользователя.

#     Args:
#         permissions: Список разрешений.

#     Raises:
#         ForbiddenException: Пользователь не имеет необходимых разрешений.
#     """

#     async def wrapper(
#         user: UserModel | None = Depends(get_current_user_or_none),
#         session: AsyncSession = Depends(get_session),
#     ):
#         if not user:
#             raise exceptions.ForbiddenException()

#         user_permissions = await UsersPermissionsService.get_user_permissions(
#             session,
#             user.id,
#         )
#         user_permissions_names = {permission.name for permission in user_permissions}

#         if not set([permission.value for permission in permissions]).issubset(
#             user_permissions_names
#         ):
#             raise exceptions.ForbiddenException()

#     return wrapper
