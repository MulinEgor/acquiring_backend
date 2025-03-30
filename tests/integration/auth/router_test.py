"""Модуль для тестирования роутера auth_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.common.routers.auth_router import router as auth_router
from src.apps.auth import schemas as auth_schemas
from src.apps.users.model import UserModel
from src.apps.users.repository import UserRepository
from src.apps.users.schemas import user_schemas
from src.lib.services.hash_service import HashService
from tests.conftest import faker
from tests.integration.conftest import BaseTestRouter


class TestAuthRouter(BaseTestRouter):
    """Класс для тестирования роутера auth_router."""

    router = auth_router

    # MARK: Login
    async def test_login_without_2fa(
        self,
        router_client: httpx.AsyncClient,
        session: AsyncSession,
    ):
        """Проверка авторизации пользователя без 2FA."""

        email, password = faker.email(), faker.password()
        await UserRepository.create(
            session=session,
            obj_in=user_schemas.UserCreateRepositorySchema(
                email=email,
                hashed_password=HashService.generate(password),
            ),
        )

        schema = user_schemas.UserLoginSchema(
            email=email,
            password=password,
        )

        response = await router_client.patch(
            url="/auth/login",
            json=schema.model_dump(),
        )

        assert response.status_code == status.HTTP_200_OK

        tokens = auth_schemas.JWTGetSchema.model_validate(response.json())

        assert tokens.access_token is not None
        assert tokens.refresh_token is not None
        assert tokens.expires_at is not None
        assert tokens.token_type == "Bearer"

    async def test_login_with_2fa(
        self, router_client: httpx.AsyncClient, session: AsyncSession, mocker
    ):
        """Проверка авторизации пользователя с 2FA, должен вернуться словарь."""

        mocker.patch(
            "src.apps.auth.services.auth_service.AuthService._send_2fa_code",
            return_value={
                "message": "Письмо с кодом подтверждения отправлено на почту."
            },
        )

        email, password = faker.email(), faker.password()
        user = await UserRepository.create(
            session=session,
            obj_in=user_schemas.UserCreateRepositorySchema(
                email=email,
                hashed_password=HashService.generate(password),
            ),
        )
        user.is_2fa_enabled = True
        await session.commit()

        schema = user_schemas.UserLoginSchema(
            email=email,
            password=password,
        )

        response = await router_client.patch(
            url="/auth/login",
            json=schema.model_dump(),
        )

        assert response.status_code == status.HTTP_200_OK

        assert isinstance(response.json(), dict)

    async def test_confirm_login_with_2fa(
        self,
        router_client: httpx.AsyncClient,
        user_db_2fa: UserModel,
        mocker,
    ):
        """Проверка подтверждения авторизации пользователя с 2FA."""

        mocker.patch(
            "src.apps.auth.services.auth_service.AuthService._check_and_delete_2fa_code",
            return_value=None,
        )

        schema = auth_schemas.TwoFactorCodeCheckSchema(
            email=user_db_2fa.email,
            code="123456",
        )

        response = await router_client.patch(
            url="/auth/2fa/login",
            json=schema.model_dump(),
        )

        assert response.status_code == status.HTTP_200_OK

        tokens = auth_schemas.JWTGetSchema.model_validate(response.json())

        assert tokens.access_token is not None
        assert tokens.refresh_token is not None

    async def test_enable_2fa_with_enabled_2fa(
        self,
        router_client: httpx.AsyncClient,
        user_db_2fa: UserModel,
        mocker,
    ):
        """Проверка включения 2FA, если 2FA уже включено."""

        mocker.patch(
            "src.apps.auth.services.auth_service.AuthService._check_and_delete_2fa_code",
            return_value=None,
        )

        schema = auth_schemas.TwoFactorCodeCheckSchema(
            email=user_db_2fa.email,
            code="123456",
        )

        response = await router_client.patch(
            url="/auth/2fa/enable",
            json=schema.model_dump(),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert isinstance(response.json(), dict)

    async def test_enable_2fa_with_disabled_2fa(
        self,
        router_client: httpx.AsyncClient,
        user_db: UserModel,
        mocker,
    ):
        """Проверка включения 2FA, если 2FA еще не включено."""

        mocker.patch(
            "src.apps.auth.services.auth_service.AuthService._check_and_delete_2fa_code",
            return_value=None,
        )

        schema = auth_schemas.TwoFactorCodeCheckSchema(
            email=user_db.email,
            code="123456",
        )

        response = await router_client.patch(
            url="/auth/2fa/enable",
            json=schema.model_dump(),
        )

        assert response.status_code == status.HTTP_200_OK

        assert isinstance(response.json(), dict)

    async def test_refresh_tokens(
        self,
        router_client: httpx.AsyncClient,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Проверка обновления токенов."""

        schema = auth_schemas.JWTRefreshSchema(
            refresh_token=user_jwt_tokens.refresh_token
        )

        response = await router_client.patch(
            url="/auth/refresh",
            json=schema.model_dump(),
        )
        jwt_data = auth_schemas.JWTGetSchema.model_validate(response.json())

        assert response.status_code == status.HTTP_200_OK
        assert jwt_data.access_token is not None
        assert jwt_data.refresh_token is not None
        assert jwt_data.expires_at is not None
        assert jwt_data.token_type == "Bearer"
