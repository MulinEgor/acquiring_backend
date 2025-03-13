"""Модуль для маршрутов авторизации пользователей."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

import src.auth.schemas as auth_schemas
import src.users.schemas as user_schemas
from src import dependencies
from src.auth.services import AuthService, JWTService

auth_router = APIRouter(prefix="/auth", tags=["Авторизация"])


# MARK: Post
@auth_router.post(
    "/register",
    summary="Зарегистрировать пользователя.",
    status_code=status.HTTP_201_CREATED,
)
async def register_route(
    schema: user_schemas.UserCreateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
) -> auth_schemas.JWTGetSchema:
    """
    Зарегистрировать пользователя.

    Доступно неавторизованному пользователю.

    Raises:
        UserAlreadyExistsException: Пользователь уже существует.
    """

    return await AuthService.register(session, schema)


# MARK: Patch
@auth_router.patch(
    "/login",
    summary="Авторизовать пользователя.",
    status_code=status.HTTP_200_OK,
)
async def login_route(
    schema: user_schemas.UserLoginSchema,
    session: AsyncSession = Depends(dependencies.get_session),
) -> auth_schemas.JWTGetSchema:
    """
    Авторизовать пользователя.

    Доступно неавторизованному пользователю.

    Raises:
        UserNotFoundException: Пользователь не найден.
    """

    return await AuthService.login(session, schema)


@auth_router.patch(
    "/refresh",
    summary="Обновить access_token и refresh_token.",
    status_code=status.HTTP_200_OK,
)
async def refresh_tokens_route(
    tokens_data: auth_schemas.JWTRefreshSchema,
    session: AsyncSession = Depends(dependencies.get_session),
) -> auth_schemas.JWTGetSchema:
    """
    Получить `access_token` и `refresh_token`, передав верный `refresh_token`.

    Доступно неавторизованному пользователю.

    Raises:
        InvalidTokenException: Невалидный токен `HTTP_401_UNAUTHORIZED`.
        TokenExpiredException: Время действия токена истекло `HTTP_401_UNAUTHORIZED`.
        UserNotFoundException: Пользователь не найден.
    """

    return await JWTService.refresh_tokens(session, tokens_data)
