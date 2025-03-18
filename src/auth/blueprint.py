"""Модуль для маршрутов авторизации пользователей."""

from sanic import Blueprint, Request
from sanic_ext import openapi

import src.auth.schemas as auth_schemas
import src.users.schemas as user_schemas
from src.auth.services.auth_service import AuthService
from src.auth.services.jwt_service import JWTService
from src.responses import api_response

bp = Blueprint(
    "Auth",
    url_prefix="/auth",
)


# MARK: Patch
@bp.patch("/login")
@openapi.summary("Авторизоваться")
@openapi.body(
    description="Данные для авторизации",
    content=user_schemas.UserLoginSchema,
    validate=True,
)
@openapi.response(
    status=200,
    description="JWT токены",
    content=auth_schemas.JWTGetSchema,
)
@openapi.response(
    status=202,
    description="Требуется подтверждение 2FA",
    content=dict[str, str],
)
async def login_route(
    request: Request,
    body: user_schemas.UserLoginSchema,
):
    """
    Войти в систему.
    Если у пользователя включена 2FA, то после вызова будет отправлен код на почту,
    который необходимо будет ввести в ендпоинт `/2fa/login/confirm`.

    Не требуется разрешений.
    """
    async with request.app.ctx.get_db_session() as session:
        return api_response(await AuthService.login(session, body))


@bp.patch("/2fa/login")
@openapi.summary("Ввести код после попытки входа.")
@openapi.body(
    description="Код для подтверждения 2FA",
    content=auth_schemas.TwoFactorCodeCheckSchema,
    validate=True,
)
@openapi.response(
    status=200,
    description="JWT токены",
    content=auth_schemas.JWTGetSchema,
)
async def login_2fa_route(
    request: Request,
    body: auth_schemas.TwoFactorCodeCheckSchema,
):
    """
    Ввести код после попытки входа.

    Не требуется разрешений.
    """
    async with request.app.ctx.get_db_session() as session:
        return api_response(await AuthService.login_2fa(session, body))


@bp.patch("/2fa/send")
@openapi.summary("Отправить код для 2FA.")
@openapi.body(
    description="Email пользователя",
    content=auth_schemas.TwoFactorCodeSendSchema,
    validate=True,
)
@openapi.response(
    status=202,
    description="Сообщение о включении 2FA или о том,\
        что письмо с кодом подтверждения уже отправлено.",
    content=dict[str, str],
)
async def send_2fa_code_route(
    request: Request,
    body: auth_schemas.TwoFactorCodeSendSchema,
):
    """
    Отправить код для 2FA.
    Можно отправить вне зависимости от того, включена 2FA или нет.
    Используется для включения, выключения 2FA или входа.

    Не требуется разрешений.
    """
    async with request.app.ctx.get_db_session() as session:
        return api_response(
            await AuthService.send_2fa_code(session, body.email), status=202
        )


@bp.patch("/2fa/enable")
@openapi.summary("Включить 2FA.")
@openapi.body(
    description="Код для подтверждения 2FA",
    content=auth_schemas.TwoFactorCodeCheckSchema,
    validate=True,
)
@openapi.response(
    status=202,
    description="Сообщение о включении 2FA.",
    content=dict[str, str],
)
async def enable_2fa_confirm_route(
    request: Request,
    body: auth_schemas.TwoFactorCodeCheckSchema,
):
    """
    Чтобы включить 2FA, нужно сначала отправить код на почту,
    после чего передать его в эндпоинт.

    Не требуется разрешений.
    """
    async with request.app.ctx.get_db_session() as session:
        return api_response(
            await AuthService.enable_or_disable_2fa(session, body, should_enable=True),
            status=202,
        )


@bp.patch("/2fa/disable")
@openapi.summary("Выключить 2FA.")
@openapi.body(
    description="Код для подтверждения 2FA",
    content=auth_schemas.TwoFactorCodeCheckSchema,
    validate=True,
)
@openapi.response(
    status=202,
    description="Сообщение о выключении 2FA.",
    content=dict[str, str],
)
async def disable_2fa_confirm_route(
    request: Request,
    body: auth_schemas.TwoFactorCodeCheckSchema,
):
    """
    Чтобы выключить 2FA, нужно сначала отправить код на почту,
    после чего передать его в эндпоинт.

    Не требуется разрешений.
    """
    async with request.app.ctx.get_db_session() as session:
        return api_response(
            await AuthService.enable_or_disable_2fa(session, body, should_enable=False),
            status=202,
        )


@bp.patch("/refresh")
@openapi.summary("Обновить access_token и refresh_token.")
@openapi.body(
    description="JWT токены",
    content=auth_schemas.JWTRefreshSchema,
    validate=True,
)
@openapi.response(
    status=200,
    description="JWT токены",
    content=auth_schemas.JWTGetSchema,
)
async def refresh_tokens_route(
    request: Request,
    body: auth_schemas.JWTRefreshSchema,
):
    """
    Обновить access_token и refresh_token.

    Не требуется разрешений.
    """
    async with request.app.ctx.get_db_session() as session:
        return api_response(await JWTService.refresh_tokens(session, body))
