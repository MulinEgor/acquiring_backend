"""Тесты для роутера permissions."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.routers.requisites_router import router as admin_requisites_router
from src.api.trader.routers.requisites_router import router as trader_requisites_router
from src.apps.auth import schemas as auth_schemas
from src.apps.requisites import schemas as requisite_schemas
from src.apps.requisites.models import RequisiteModel
from src.apps.requisites.repository import RequisiteRepository
from src.apps.users.models import UserModel
from src.core import constants
from tests.integration.conftest import BaseTestRouter


# MARK: Trader
class TestTraderRequisitesRouter(BaseTestRouter):
    """Тесты для роутера requisites трейдера."""

    router = trader_requisites_router

    # MARK: Create
    async def test_create_requisite_trader(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_create_data: requisite_schemas.RequisiteCreateSchema,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
        session: AsyncSession,
    ):
        """
        Попытка создать реквизит трейдером.
        """

        response = await router_client.post(
            "/requisites/me",
            json=requisite_trader_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        requisite = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite is not None
        assert requisite.user_id == user_trader_db.id
        assert requisite.full_name == requisite_trader_create_data.full_name
        assert requisite.phone_number == requisite_trader_create_data.phone_number
        assert requisite.bank_name == requisite_trader_create_data.bank_name

        data = await RequisiteRepository.get_all(session=session, limit=100, offset=0)

        assert len(data) == 1

    # MARK: Get
    async def test_get_requisite_trader(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
        session: AsyncSession,
    ):
        """Попытка получить реквизит трейдером."""

        response = await router_client.get(
            f"/requisites/me/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        requisite = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite is not None
        assert requisite.user_id == user_trader_db.id
        assert requisite.full_name == requisite_trader_db.full_name
        assert requisite.phone_number == requisite_trader_db.phone_number
        assert requisite.bank_name == requisite_trader_db.bank_name

    async def test_get_requisite_not_traders(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_admin_db: UserModel,
        session: AsyncSession,
    ):
        """Попытка получить реквизит, созданный не трейдером."""
        requisite_trader_db.user_id = user_admin_db.id
        await session.commit()

        response = await router_client.get(
            f"/requisites/me/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_requisites_trader_no_query(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
    ):
        """Попытка получить все реквизиты трейдером без параметров."""
        response = await router_client.get(
            "/requisites/me",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = requisite_schemas.RequisiteListGetSchema(**response.json())

        assert len(schema.data) == 1
        assert schema.data[0].id == requisite_trader_db.id
        assert schema.data[0].user_id == user_trader_db.id

    async def test_get_requisites_trader_query(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
    ):
        """Попытка получить все реквизиты трейдером с параметрами."""
        query_params = requisite_schemas.RequisitePaginationSchema(
            full_name=requisite_trader_db.full_name[:2],
        )

        response = await router_client.get(
            "/requisites/me",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_200_OK

        schema = requisite_schemas.RequisiteListGetSchema(**response.json())

        assert len(schema.data) == 1
        assert schema.data[0].id == requisite_trader_db.id
        assert schema.data[0].user_id == user_trader_db.id

    # MARK: Update
    async def test_update_requisite_trader(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
        requisite_trader_update_data: requisite_schemas.RequisiteUpdateSchema,
        session: AsyncSession,
    ):
        """Попытка обновить реквизит трейдером."""

        response = await router_client.put(
            f"/requisites/me/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=requisite_trader_update_data.model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        assert schema.id == requisite_trader_db.id
        assert schema.user_id == user_trader_db.id
        assert schema.full_name == requisite_trader_update_data.full_name

        requisite_db = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite_db is not None
        assert requisite_db.user_id == user_trader_db.id
        assert requisite_db.full_name == requisite_trader_update_data.full_name

    # MARK: Delete
    async def test_delete_requisite_trader(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Попытка удалить реквизит трейдером."""

        response = await router_client.delete(
            f"/requisites/me/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        data = await RequisiteRepository.get_all(session=session, limit=100, offset=0)

        assert len(data) == 0


# MARK: Admin
class TestAdminRequisitesRouter(BaseTestRouter):
    """Тесты для админского роутера requisites."""

    router = admin_requisites_router

    # MARK: Create
    async def test_create_requisite_admin(
        self,
        router_client: httpx.AsyncClient,
        requisite_admin_create_data: requisite_schemas.RequisiteCreateAdminSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """
        Попытка создать реквизит администратором.
        """

        response = await router_client.post(
            "/requisites",
            json=requisite_admin_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        requisite = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite is not None
        assert requisite.user_id == requisite_admin_create_data.user_id
        assert requisite.full_name == requisite_admin_create_data.full_name
        assert requisite.phone_number == requisite_admin_create_data.phone_number
        assert requisite.bank_name == requisite_admin_create_data.bank_name

        data = await RequisiteRepository.get_all(session=session, limit=100, offset=0)

        assert len(data) == 1

    async def test_create_requisite_non_admin(
        self,
        router_client: httpx.AsyncClient,
        requisite_admin_create_data: requisite_schemas.RequisiteCreateAdminSchema,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """
        Попытка создать реквизит администратором.
        """

        response = await router_client.post(
            "/requisites",
            json=requisite_admin_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        data = await RequisiteRepository.get_all(session=session, limit=100, offset=0)

        assert len(data) == 0

    # MARK: Get
    async def test_get_requisite_admin(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Попытка получить реквизит администратором."""

        response = await router_client.get(
            f"/requisites/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        requisite = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite is not None
        assert requisite.user_id == requisite_trader_db.user_id
        assert requisite.full_name == requisite_trader_db.full_name
        assert requisite.phone_number == requisite_trader_db.phone_number
        assert requisite.bank_name == requisite_trader_db.bank_name

    async def test_get_requisites_admin_no_query(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
    ):
        """Попытка получить все реквизиты администратором без параметров."""
        response = await router_client.get(
            "/requisites",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = requisite_schemas.RequisiteListGetSchema(**response.json())

        assert len(schema.data) == 1
        assert schema.data[0].id == requisite_trader_db.id
        assert schema.data[0].user_id == user_trader_db.id

    async def test_get_requisites_admin_query(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
    ):
        """Попытка получить все реквизиты администратором с параметрами."""
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

        assert len(schema.data) == 1
        assert schema.data[0].id == requisite_trader_db.id
        assert schema.data[0].user_id == user_trader_db.id

    # MARK: Update
    async def test_update_requisite_admin(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        requisite_admin_update_data: requisite_schemas.RequisiteUpdateAdminSchema,
        session: AsyncSession,
    ):
        """Попытка обновить реквизит администратором."""

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
    async def test_delete_requisite_admin(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Попытка удалить реквизит админоом."""

        response = await router_client.delete(
            f"/requisites/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        data = await RequisiteRepository.get_all(session=session, limit=100, offset=0)

        assert len(data) == 0
