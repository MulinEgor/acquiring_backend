"""Модуль для тестирования роутера src.users.routers.auth_router"""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

import src.auth.schemas as auth_schemas
import src.users.schemas as user_schemas
from src.auth.router import auth_router
from src.roles.models import RoleModel
from src.users.repository import UserRepository
from src.utils import hash as utils
from tests.conftest import faker
from tests.integration.conftest import BaseTestRouter


class TestAuthRouter(BaseTestRouter):
    """Класс для тестирования роутера auth_router."""

    router = auth_router

    # MARK: Patch
    async def test_login(
        self,
        router_client: httpx.AsyncClient,
        session: AsyncSession,
        merchant_role_db: RoleModel,
    ):
        """Проверка авторизации пользователя."""

        email, password = faker.email(), faker.password()
        await UserRepository.create(
            session=session,
            obj_in=user_schemas.UserCreateRepositorySchema(
                email=email,
                hashed_password=utils.get_hash(password),
                role_id=merchant_role_db.id,
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
