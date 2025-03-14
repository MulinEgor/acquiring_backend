"""Тесты для роутера roles."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src import constants
from src.auth import schemas as auth_schemas
from src.roles import schemas
from src.roles.models import RoleModel
from src.roles.repository import RoleRepository
from src.roles.router import roles_router
from tests.integration.conftest import BaseTestRouter


class TestRolesRouter(BaseTestRouter):
    """Тесты для роутера roles."""

    router = roles_router

    # MARK: Create
    async def test_create_role_non_admin(
        self,
        router_client: httpx.AsyncClient,
        role_create_data: schemas.RoleCreateSchema,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """
        Попытка создать роль без прав администратора.
        Никакие роли не должны быть созданы.
        """

        response = await router_client.post(
            "/roles",
            json=role_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        role = await RoleRepository.get_one_or_none(
            session=session,
            name=role_create_data.name,
        )
        assert role is None

    async def test_create_role_admin(
        self,
        router_client: httpx.AsyncClient,
        role_create_data: schemas.RoleCreateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Создание роли администратором.
        """

        response = await router_client.post(
            "/roles",
            json=role_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = schemas.RoleGetSchema(**response.json())
        assert data.name == role_create_data.name

    # MARK: Get
    async def test_get_role_by_id_admin(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        admin_role_db: RoleModel,
    ):
        """Получение роли администратором."""

        response = await router_client.get(
            f"/roles/{admin_role_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = schemas.RoleGetSchema(**response.json())
        assert str(data.id) == str(admin_role_db.id)
        assert data.name == admin_role_db.name

    async def test_get_all_roles_admin_no_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        admin_role_db: RoleModel,
    ):
        """Получение всех ролей администратором без учета фильтрации."""

        response = await router_client.get(
            "/roles",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = schemas.RoleListGetSchema(**response.json())

        assert data.count == 1
        assert str(data.data[0].id) == str(admin_role_db.id)
        assert data.data[0].name == admin_role_db.name

    async def test_get_all_roles_admin_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        admin_role_db: RoleModel,
    ):
        """Получение всех ролей администратором с учетом фильтрации."""

        query_params = schemas.RolePaginationSchema(name="adm")

        response = await router_client.get(
            "/roles",
            params=query_params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = schemas.RoleListGetSchema(**response.json())

        assert data.count == 1
        assert str(data.data[0].id) == str(admin_role_db.id)
        assert data.data[0].name == admin_role_db.name

    # MARK: Update
    async def test_update_role_admin(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        admin_role_db: RoleModel,
    ):
        """Обновление роли администратором."""

        response = await router_client.put(
            f"/roles/{admin_role_db.id}",
            json={"name": "new_name"},
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        data = schemas.RoleGetSchema(**response.json())
        assert str(data.id) == str(admin_role_db.id)
        assert data.name == "new_name"

    # MARK: Delete
    async def test_delete_role_admin(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        merchant_role_db: RoleModel,
        session: AsyncSession,
    ):
        """Удаление роли администратором."""

        response = await router_client.delete(
            f"/roles/{merchant_role_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        role = await RoleRepository.get_one_or_none(
            session=session,
            name=merchant_role_db.name,
        )
        assert role is None
