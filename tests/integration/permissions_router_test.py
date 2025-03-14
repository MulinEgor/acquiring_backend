"""Тесты для роутера permissions."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src import constants
from src.auth import schemas as auth_schemas
from src.permissions import schemas
from src.permissions.models import PermissionModel
from src.permissions.repository import PermissionRepository
from src.permissions.router import permissions_router
from tests.integration.conftest import BaseTestRouter


class TestPermissionsRouter(BaseTestRouter):
    """Тесты для роутера permissions."""

    router = permissions_router

    # MARK: Create
    async def test_create_permission_non_admin(
        self,
        router_client: httpx.AsyncClient,
        permission_create_data: schemas.PermissionCreateSchema,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """
        Попытка создать разрешение без прав администратора.
        Никакие разрешения не должны быть созданы.
        """

        response = await router_client.post(
            "/permissions",
            json=permission_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        permission = await PermissionRepository.get_one_or_none(
            session=session,
            name=permission_create_data.name,
        )
        assert permission is None

    async def test_create_permission_admin(
        self,
        router_client: httpx.AsyncClient,
        permission_create_data: schemas.PermissionCreateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Создание разрешения администратором.
        """

        response = await router_client.post(
            "/permissions",
            json=permission_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = schemas.PermissionGetSchema(**response.json())
        assert data.name == permission_create_data.name

    # MARK: Get
    async def test_get_permission_by_id_admin(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        permission_db: PermissionModel,
    ):
        """Получение разрешения администратором."""

        response = await router_client.get(
            f"/permissions/{permission_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = schemas.PermissionGetSchema(**response.json())
        assert str(data.id) == str(permission_db.id)
        assert data.name == permission_db.name

    async def test_get_all_permissions_admin_no_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        permission_db: PermissionModel,
    ):
        """Получение всех разрешений администратором без учета фильтрации."""

        response = await router_client.get(
            "/permissions",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = schemas.PermissionListGetSchema(**response.json())

        assert data.count == 1
        assert str(data.data[0].id) == str(permission_db.id)
        assert data.data[0].name == permission_db.name

    async def test_get_all_permissions_admin_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        permission_db: PermissionModel,
    ):
        """Получение всех разрешений администратором с учетом фильтрации."""

        query_params = schemas.PermissionPaginationSchema(name=permission_db.name[:2])

        response = await router_client.get(
            "/permissions",
            params=query_params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = schemas.PermissionListGetSchema(**response.json())

        assert data.count == 1
        assert str(data.data[0].id) == str(permission_db.id)
        assert data.data[0].name == permission_db.name

    # MARK: Update
    async def test_update_permission_admin(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        permission_db: PermissionModel,
    ):
        """Обновление разрешения администратором."""

        response = await router_client.put(
            f"/permissions/{permission_db.id}",
            json={"name": "new_name"},
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        data = schemas.PermissionGetSchema(**response.json())
        assert str(data.id) == str(permission_db.id)
        assert data.name == "new_name"

    # MARK: Delete
    async def test_delete_permission_admin(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        permission_db: PermissionModel,
        session: AsyncSession,
    ):
        """Удаление разрешения администратором."""

        response = await router_client.delete(
            f"/permissions/{permission_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        permission = await PermissionRepository.get_one_or_none(
            session=session,
            name=permission_db.name,
        )
        assert permission is None
