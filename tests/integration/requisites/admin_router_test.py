"""Тесты для роутера src.api.admin.routers.requisites_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.routers.requisites_router import router as requisites_router
from src.apps.auth import schemas as auth_schemas
from src.apps.requisites import schemas as requisite_schemas
from src.apps.requisites.model import RequisiteModel
from src.apps.requisites.repository import RequisiteRepository
from src.apps.users.model import UserModel
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestAdminRequisitesRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = requisites_router

    # MARK: Post
    async def test_create_requisite(
        self,
        router_client: httpx.AsyncClient,
        requisite_admin_create_data: requisite_schemas.RequisiteCreateAdminSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Создание реквизита."""

        response = await router_client.post(
            "/requisites",
            json=requisite_admin_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        requisite_db = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite_db is not None
        assert requisite_db.user_id == requisite_admin_create_data.user_id
        assert requisite_db.full_name == requisite_admin_create_data.full_name
        assert requisite_db.phone_number == requisite_admin_create_data.phone_number
        assert requisite_db.bank_name == requisite_admin_create_data.bank_name

    async def test_create_requisite_not_authorized(
        self,
        router_client: httpx.AsyncClient,
        requisite_admin_create_data: requisite_schemas.RequisiteCreateAdminSchema,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Создание реквизита не авторизованным пользователем."""

        response = await router_client.post(
            "/requisites",
            json=requisite_admin_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        requisites_db = await RequisiteRepository.get_all(session=session)
        assert len(requisites_db) == 0

    # MARK: Get
    async def test_get_requisite(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Получение реквизита."""

        response = await router_client.get(
            f"/requisites/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        requisite_db = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite_db is not None
        assert requisite_db.user_id == requisite_trader_db.user_id
        assert requisite_db.full_name == requisite_trader_db.full_name
        assert requisite_db.phone_number == requisite_trader_db.phone_number
        assert requisite_db.bank_name == requisite_trader_db.bank_name

    async def test_get_requisites_no_query(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
    ):
        """Получение всех реквизитов администратором без пагинации и фильтрации."""

        response = await router_client.get(
            "/requisites",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = requisite_schemas.RequisiteListGetSchema(**response.json())

        assert len(schema.data) >= 1

    async def test_get_requisites_query(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
    ):
        """Получение всех реквизитов с пагинацией и фильтрацией."""

        query_params = requisite_schemas.RequisitePaginationAdminSchema(
            user_id=user_trader_db.id,
        )

        response = await router_client.get(
            "/requisites",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_200_OK

        schema = requisite_schemas.RequisiteListGetSchema(**response.json())

        assert len(schema.data) >= 1

    # MARK: Put
    async def test_update_requisite(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        requisite_admin_update_data: requisite_schemas.RequisiteUpdateAdminSchema,
        session: AsyncSession,
    ):
        """Обновление реквизита."""

        response = await router_client.put(
            f"/requisites/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
            json=requisite_admin_update_data.model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        assert schema.id == requisite_trader_db.id
        assert schema.user_id == requisite_admin_update_data.user_id

        requisite = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite is not None
        assert requisite.user_id == requisite_admin_update_data.user_id

    # MARK: Delete
    async def test_delete_requisite(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Удаление реквизита."""

        response = await router_client.delete(
            f"/requisites/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        requisites_db = await RequisiteRepository.get_all(session=session)
        assert len(requisites_db) == 0
