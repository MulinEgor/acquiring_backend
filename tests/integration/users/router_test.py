"""
Модуль для тестирования роутера src.api.admin.routers.users_router.
Этот роутер также включает в себя роутер src.api.common.routers.users_router.
"""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.routers.users_router import router as users_router
from src.apps.auth import schemas as auth_schemas
from src.apps.users import schemas as user_schemas
from src.apps.users.model import UserModel
from src.apps.users.repository import UserRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestUserRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = users_router

    # MARK: Get
    async def test_get_current_user(
        self,
        router_client: httpx.AsyncClient,
        user_db: UserModel,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение информации о текущем пользователе."""

        response = await router_client.get(
            url="/users/me",
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = user_schemas.UserGetSchema(**response.json())

        assert data.id == user_db.id
        assert data.email == user_db.email

    async def test_get_user_by_id(
        self,
        router_client: httpx.AsyncClient,
        user_admin_db: UserModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение информации о пользователе по id."""

        response = await router_client.get(
            url=f"/users/{user_admin_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = user_schemas.UserGetSchema(**response.json())

        assert data.id == user_admin_db.id
        assert data.email == user_admin_db.email

    async def test_get_users_by_admin_no_query(
        self,
        session: AsyncSession,
        router_client: httpx.AsyncClient,
        user_db: UserModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение списка пользователей без учета фильтрации."""

        response = await router_client.get(
            url="/users",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        users_data = user_schemas.UsersListGetSchema(**response.json())

        users_count = await UserRepository.count(session=session)
        assert users_data.count == users_count

        first_user_db = await UserRepository.get_one_or_none(
            session=session, id=users_data.data[0].id
        )
        assert first_user_db is not None

        assert users_data.data[0].email == first_user_db.email
        assert users_data.data[0].id == first_user_db.id

    async def test_get_users_by_admin_query(
        self,
        router_client: httpx.AsyncClient,
        user_db: UserModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение списка пользователей с учетом фильтрации."""

        params = user_schemas.UsersPaginationSchema(email=user_db.email)

        response = await router_client.get(
            url="/users",
            params=params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        users_data = user_schemas.UsersListGetSchema(**response.json())

        assert users_data.data[0].email == user_db.email
        assert users_data.data[0].id == user_db.id

    # MARK: Post
    async def test_create_user_by_admin_route(
        self,
        session: AsyncSession,
        router_client: httpx.AsyncClient,
        user_create_data: user_schemas.UserCreateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Создание пользователя."""

        response = await router_client.post(
            url="/users",
            json=user_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_201_CREATED

        created_user = user_schemas.UserCreatedGetSchema(**response.json())
        assert created_user.email == user_create_data.email

        created_user_db = await UserRepository.get_one_or_none(
            session=session, id=created_user.id
        )
        assert created_user_db is not None

    # MARK: Put
    async def test_update_user_by_admin(
        self,
        router_client: httpx.AsyncClient,
        user_db: UserModel,
        user_update_data: user_schemas.UserUpdateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Обновление данных пользователя."""

        response = await router_client.put(
            url=f"/users/{user_db.id}",
            json=user_update_data.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        updated_user = user_schemas.UserGetSchema(**response.json())

        assert updated_user.id == user_db.id
        assert updated_user.email == user_update_data.email

        user_db = await UserRepository.get_one_or_none(session=session, id=user_db.id)
        assert user_db is not None
        assert user_db.email == user_update_data.email

    # MARK: Delete
    async def test_delete_user_by_admin(
        self,
        router_client: httpx.AsyncClient,
        session: AsyncSession,
        user_db: UserModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Удаление пользователя."""

        response = await router_client.delete(
            url=f"/users/{user_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        deleted_user = await UserRepository.get_one_or_none(
            session=session,
            id=user_db.id,
        )

        assert deleted_user is None
