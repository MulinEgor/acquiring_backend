"""Модуль для маршрутов авторизации пользователей."""

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

import src.apps.auth.schemas as auth_schemas
from src.apps.auth.services.auth_service import AuthService
from src.apps.auth.services.jwt_service import JWTService
from src.apps.users.schemas import user_schemas
from src.core import dependencies

router = APIRouter(prefix="/auth", tags=["Авторизация"])


# MARK: Patch
@router.patch(
    "/login",
    summary="Авторизоваться.",
    status_code=status.HTTP_200_OK,
)
async def login_route(
    schema: user_schemas.UserLoginSchema,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(dependencies.get_session),
) -> auth_schemas.JWTGetSchema | dict[str, str]:
    """
    Войти в систему.
    Если у пользователя включена 2FA, то после вызова будет отправлен код на почту,
    который необходимо будет ввести в ендпоинт `/2fa/login/confirm`.

    Не требуется разрешений.
    """
    return await AuthService.login(session, background_tasks, schema)


@router.patch(
    "/2fa/login",
    summary="Ввести код после попытки входа.",
    status_code=status.HTTP_200_OK,
)
async def login_2fa_route(
    code_schema: auth_schemas.TwoFactorCodeCheckSchema,
    session: AsyncSession = Depends(dependencies.get_session),
) -> auth_schemas.JWTGetSchema:
    """
    Ввести код после попытки входа.

    Не требуется разрешений.
    """
    return await AuthService.login_2fa(session, code_schema)


@router.patch(
    "/2fa/send",
    summary="Отправить код для 2FA.",
    status_code=status.HTTP_200_OK,
)
async def send_2fa_code_route(
    schema: auth_schemas.TwoFactorCodeSendSchema,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Отправить код для 2FA.
    Можно отправить вне зависимости от того, включена 2FA или нет.
    Используется для включения, выключения 2FA или входа.

    Не требуется разрешений.
    """
    return await AuthService.send_2fa_code(
        session, background_tasks, email=schema.email
    )


@router.patch(
    "/2fa/enable",
    summary="Включить 2FA.",
    status_code=status.HTTP_200_OK,
)
async def enable_2fa_confirm_route(
    code_schema: auth_schemas.TwoFactorCodeCheckSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Чтобы включить 2FA, нужно сначала отправить код на почту,
    после чего передать его в эндпоинт.

    Не требуется разрешений.
    """
    return await AuthService.enable_or_disable_2fa(
        session, code_schema, should_enable=True
    )


@router.patch(
    "/2fa/disable",
    summary="Выключить 2FA.",
    status_code=status.HTTP_200_OK,
)
async def disable_2fa_confirm_route(
    code_schema: auth_schemas.TwoFactorCodeCheckSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Чтобы выключить 2FA, нужно сначала отправить код на почту,
    после чего передать его в эндпоинт.

    Не требуется разрешений.
    """
    return await AuthService.enable_or_disable_2fa(
        session, code_schema, should_enable=False
    )


@router.patch(
    "/refresh",
    summary="Обновить access_token и refresh_token.",
    status_code=status.HTTP_200_OK,
)
async def refresh_tokens_route(
    token_schema: auth_schemas.JWTRefreshSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Обновить access_token и refresh_token.

    Не требуется разрешений.
    """
    return await JWTService.refresh_tokens(session, token_schema)
