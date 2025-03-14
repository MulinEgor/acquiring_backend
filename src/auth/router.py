"""Модуль для маршрутов авторизации пользователей."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

import src.auth.schemas as auth_schemas
import src.users.schemas as user_schemas
from src import dependencies
from src.auth.services.auth_service import AuthService
from src.auth.services.jwt_service import JWTService

auth_router = APIRouter(prefix="/auth", tags=["Авторизация"])


# MARK: Patch
@auth_router.patch(
    "/login",
    summary="Авторизоваться.",
    status_code=status.HTTP_200_OK,
)
async def login_route(
    schema: user_schemas.UserLoginSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Авторизоваться.

    Требуется разрешение: `войти`.
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
):
    """
    Обновить access_token и refresh_token.

    Требуется разрешение: `обновить refresh_token`.
    """
    return await JWTService.refresh_tokens(session, tokens_data)
