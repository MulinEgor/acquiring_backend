"""Модуль для тестирования роутера src.users.routes.user_routes"""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

import src.auth.schemas as auth_schemas
import src.users.schemas as user_schemas
from src import constants
from src.users import UserModel, UserRepository, user_router
from tests.integration.conftest import BaseTestRouter


class TestUserRouter(BaseTestRouter):
    """Класс для тестирования роутера user_router."""

    router = user_router

    # MARK: Get
    async def test_get_current_user(
        self,
        router_client: httpx.AsyncClient,
        user_db: UserModel,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Проверка получения информации о пользователе."""

        response = await router_client.get(
            url="/users/me",
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = user_schemas.UserGetSchema(**response.json())

        assert str(data.id) == user_db.id
        assert data.email == user_db.email

    async def test_get_user_by_id(
        self,
        router_client: httpx.AsyncClient,
        user_admin_db: UserModel,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Авторизованный пользователь может получить
        данные другого пользователя по id.
        """

        response = await router_client.get(
            url=f"/users/{user_admin_db.id}",
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = user_schemas.UserGetSchema(**response.json())

        assert str(data.id) == user_admin_db.id
        assert data.email == user_admin_db.email

    async def test_get_users_by_admin_no_query(
        self,
        session: AsyncSession,
        router_client: httpx.AsyncClient,
        user_db: UserModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Администратор может получить список
        пользователей без учета фильтрации.

        `user_db` передается для создания второго пользователя.
        """

        response = await router_client.get(
            url="/users",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        users_data = user_schemas.UserListGetSchema(**response.json())

        users_count = await UserRepository.count(session=session)
        assert users_data.count == users_count

        # Ищем первого пользователя в БД и проверяем его данные.
        first_user_db = await UserRepository.get_one_or_none(
            session=session, id=users_data.data[0].id
        )
        assert first_user_db is not None

        assert users_data.data[0].email == first_user_db.email
        assert users_data.data[0].id == first_user_db.id

    async def test_get_users_by_admin_query(
        self,
        router_client: httpx.AsyncClient,
        session: AsyncSession,
        user_db: UserModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Администратор может получить список
        пользователей с учетом учета фильтрации.
        """

        params = user_schemas.UsersQuerySchema(is_admin=False)

        response = await router_client.get(
            url="/users",
            params=params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        users_data = user_schemas.UserListGetSchema(**response.json())

        regular_users = await UserRepository.count(
            session=session,
            is_admin=False,
        )
        assert users_data.count == regular_users

        assert users_data.data[0].email == user_db.email
        assert str(users_data.data[0].id) == user_db.id

    # MARK: Post
    async def test_create_user_by_admin_route(
        self,
        session: AsyncSession,
        router_client: httpx.AsyncClient,
        user_create_data: user_schemas.UserCreateAdminSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Администратор может создать пользователя."""

        response = await router_client.post(
            url="/users",
            json=user_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_201_CREATED

        created_user = user_schemas.UserGetAdminSchema(**response.json())

        assert created_user.email == user_create_data.email
        assert created_user.is_admin is False

        created_user_db = await UserRepository.get_one_or_none(
            session=session, id=created_user.id
        )
        assert created_user_db is not None

    # MARK: Patch
    async def test_update_current_user(
        self,
        router_client: httpx.AsyncClient,
        user_db: UserModel,
        user_update_data: user_schemas.UserUpdateAdminSchema,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Пользователь может обновить данные своего аккаунта.

        Изменяем только поля `email` и `password`.
        """

        response = await router_client.patch(
            url="/users/me",
            json=user_update_data.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        updated_user = user_schemas.UserGetSchema(**response.json())

        assert str(updated_user.id) == user_db.id
        assert updated_user.email == user_update_data.email

    # MARK: Put
    async def test_update_user_by_admin(
        self,
        router_client: httpx.AsyncClient,
        user_db: UserModel,
        user_update_data: user_schemas.UserUpdateAdminSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Администратор может обновить данные другого пользователя.

        Изменяем только поля `level`, `exchange_url` и `is_admin`.
        """

        response = await router_client.put(
            url=f"/users/{user_db.id}",
            json=user_update_data.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        updated_user = user_schemas.UserGetAdminSchema(**response.json())

        assert str(updated_user.id) == user_db.id
        assert updated_user.email == user_update_data.email
        assert updated_user.is_admin == user_update_data.is_admin

    # MARK: Delete
    async def test_delete_user_by_admin(
        self,
        router_client: httpx.AsyncClient,
        session: AsyncSession,
        user_db: UserModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Администратор может удалить пользователя."""

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
