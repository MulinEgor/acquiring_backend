"""Тесты для роутера role_permission."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src import constants
from src.auth import schemas as auth_schemas
from src.roles_permissions import schemas
from src.roles_permissions.models import RolesPermissionsModel
from src.roles_permissions.repository import RolesPermissionsRepository
from src.roles_permissions.router import roles_permissions_router
from tests.integration.conftest import BaseTestRouter


class TestRolesPermissionsRouter(BaseTestRouter):
    """Тесты для роутера roles_permissions."""

    router = roles_permissions_router

    # MARK: Create
    async def test_create_role_permission_non_admin(
        self,
        router_client: httpx.AsyncClient,
        roles_permissions_create_data: schemas.RolesPermissionsCreateSchema,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """
        Попытка создать связь роли и разрешения без прав администратора.
        Никакие связи не должны быть созданы.
        """

        response = await router_client.post(
            "/roles-permissions",
            json=roles_permissions_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        role = await RolesPermissionsRepository.get_one_or_none(
            session=session,
            role_id=roles_permissions_create_data.role_id,
            permission_id=roles_permissions_create_data.permission_id,
        )
        assert role is None

    async def test_create_role_permission_admin(
        self,
        router_client: httpx.AsyncClient,
        roles_permissions_create_data: schemas.RolesPermissionsCreateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Создание связи роли и разрешения администратором.
        """

        response = await router_client.post(
            "/roles-permissions",
            json=roles_permissions_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = schemas.RolesPermissionsGetSchema(**response.json())
        assert str(data.role.id) == str(roles_permissions_create_data.role_id)
        assert str(data.permission.id) == str(
            roles_permissions_create_data.permission_id
        )

    # MARK: Get
    async def test_get_role_permission_by_id_admin(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        roles_permissions_db: RolesPermissionsModel,
    ):
        """Получение роли администратором."""

        response = await router_client.get(
            f"/roles-permissions/{roles_permissions_db.role_id}/{roles_permissions_db.permission_id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = schemas.RolesPermissionsGetSchema(**response.json())
        assert str(data.role.id) == str(roles_permissions_db.role_id)
        assert str(data.permission.id) == str(roles_permissions_db.permission_id)

    async def test_get_all_roles_admin_no_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        roles_permissions_db: RolesPermissionsModel,
    ):
        """
        Получение всех связей ролей и разрешений администратором без учета фильтрации.
        """

        response = await router_client.get(
            "/roles-permissions",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = schemas.RolesPermissionsListGetSchema(**response.json())

        assert data.count == 1
        assert str(data.data[0].role.id) == str(roles_permissions_db.role_id)
        assert str(data.data[0].permission.id) == str(
            roles_permissions_db.permission_id
        )

    async def test_get_all_roles_admin_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        roles_permissions_db: RolesPermissionsModel,
    ):
        """
        Получение всех связей ролей и разрешений администратором с учетом фильтрации.
        """

        query_params = schemas.RolesPermissionsPaginationSchema(
            role_id=roles_permissions_db.role_id,
            permission_id=roles_permissions_db.permission_id,
        )

        response = await router_client.get(
            "/roles-permissions",
            params=query_params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = schemas.RolesPermissionsListGetSchema(**response.json())

        assert data.count == 1
        assert str(data.data[0].role.id) == str(roles_permissions_db.role_id)
        assert str(data.data[0].permission.id) == str(
            roles_permissions_db.permission_id
        )

    # MARK: Delete
    async def test_delete_role_permission_admin(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        roles_permissions_db: RolesPermissionsModel,
        session: AsyncSession,
    ):
        """Удаление связи роли и разрешения администратором."""

        response = await router_client.delete(
            f"/roles-permissions/{roles_permissions_db.role_id}/{roles_permissions_db.permission_id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        role = await RolesPermissionsRepository.get_one_or_none(
            session=session,
            role_id=roles_permissions_db.role_id,
            permission_id=roles_permissions_db.permission_id,
        )
        assert role is None
