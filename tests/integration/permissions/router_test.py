"""Модуль для тестирования роутера src.api.admin.routers.permissions_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.routers.permissions_router import router as permissions_router
from src.apps.auth import schemas as auth_schemas
from src.apps.permissions import schemas
from src.apps.permissions.model import PermissionModel
from src.apps.permissions.repository import PermissionRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestPermissionsRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = permissions_router

    # MARK: Post
    async def test_create_permission_not_authorized(
        self,
        router_client: httpx.AsyncClient,
        permission_create_data: schemas.PermissionCreateSchema,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Создание разрешения, не иммея на это права."""

        response = await router_client.post(
            "/permissions",
            json=permission_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        permission_db = await PermissionRepository.get_one_or_none(
            session=session,
            name=permission_create_data.name,
        )
        assert permission_db is None

    async def test_create_permission(
        self,
        router_client: httpx.AsyncClient,
        permission_create_data: schemas.PermissionCreateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Создание разрешения."""

        response = await router_client.post(
            "/permissions",
            json=permission_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = schemas.PermissionGetSchema(**response.json())
        assert schema.name == permission_create_data.name

        permission_db = await PermissionRepository.get_one_or_none(
            session=session,
            name=permission_create_data.name,
        )
        assert permission_db is not None
        assert permission_db.name == permission_create_data.name

    # MARK: Get
    async def test_get_permission_by_id(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        permission_db: PermissionModel,
    ):
        """Получение разрешения."""

        response = await router_client.get(
            f"/permissions/{permission_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = schemas.PermissionGetSchema(**response.json())
        assert schema.id == permission_db.id
        assert schema.name == permission_db.name

    async def test_get_all_permissions_no_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        permission_db: PermissionModel,
    ):
        """Получение всех разрешений без учета фильтрации."""

        response = await router_client.get(
            "/permissions",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = schemas.PermissionListGetSchema(**response.json())

        assert schema.count >= 1

    async def test_get_all_permissions_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        permission_db: PermissionModel,
    ):
        """Получение всех разрешений с учетом фильтрации."""

        query_params = schemas.PermissionPaginationSchema(name=permission_db.name[:2])

        response = await router_client.get(
            "/permissions",
            params=query_params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = schemas.PermissionListGetSchema(**response.json())

        assert schema.count == 1
        assert schema.data[0].id == permission_db.id
        assert schema.data[0].name == permission_db.name

    # MARK: Put
    async def test_update_permission(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        permission_db: PermissionModel,
    ):
        """Обновление разрешения."""

        update_data = schemas.PermissionCreateSchema(name="new_name")

        response = await router_client.put(
            f"/permissions/{permission_db.id}",
            json=update_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        schema = schemas.PermissionGetSchema(**response.json())
        assert schema.id == permission_db.id
        assert schema.name == update_data.name

    # MARK: Delete
    async def test_delete_permission(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        permission_db: PermissionModel,
        session: AsyncSession,
    ):
        """Удаление разрешения."""

        response = await router_client.delete(
            f"/permissions/{permission_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        permission_db = await PermissionRepository.get_one_or_none(
            session=session,
            name=permission_db.name,
        )
        assert permission_db is None
