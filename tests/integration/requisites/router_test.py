"""Тесты для роутера src.api.user.routers.users.requisites_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.user.routers.users.requisites_router import router as requisites_router
from src.apps.auth import schemas as auth_schemas
from src.apps.requisites import schemas as requisite_schemas
from src.apps.requisites.model import RequisiteModel
from src.apps.requisites.repository import RequisiteRepository
from src.apps.users.model import UserModel
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestRequisitesRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = requisites_router

    # MARK: Post
    async def test_create_requisite(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_create_data: requisite_schemas.RequisiteCreateSchema,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db_with_sbp: UserModel,
        session: AsyncSession,
    ):
        """Создание реквизита трейдером."""

        response = await router_client.post(
            "/requisites",
            json=requisite_trader_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        requisite_db = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite_db is not None
        assert requisite_db.user_id == user_trader_db_with_sbp.id
        assert requisite_db.full_name == requisite_trader_create_data.full_name
        assert requisite_db.phone_number == requisite_trader_create_data.phone_number
        assert requisite_db.bank_name == requisite_trader_create_data.bank_name

    # MARK: Get
    async def test_get_requisite(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db_with_sbp: UserModel,
        session: AsyncSession,
    ):
        """Получение реквизита трейдера."""

        response = await router_client.get(
            f"/requisites/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        requisite = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite is not None
        assert requisite.user_id == user_trader_db_with_sbp.id
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
        """Получение реквизита, созданного не трейдером."""

        requisite_trader_db.user_id = user_admin_db.id
        await session.commit()

        response = await router_client.get(
            f"/traders/requisites/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_requisites_no_query(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db_with_sbp: UserModel,
    ):
        """Получение всех реквизитов трейдера без параметров."""

        response = await router_client.get(
            "/requisites",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        requisite_schemas.RequisiteListGetSchema(**response.json())

    async def test_get_requisites_query(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db_with_sbp: UserModel,
    ):
        """Получение всех реквизитов трейдера с параметрами."""

        query_params = requisite_schemas.RequisitePaginationSchema(
            full_name=requisite_trader_db.full_name[:2],
        )

        response = await router_client.get(
            "/requisites",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_200_OK

        schema = requisite_schemas.RequisiteListGetSchema(**response.json())

        assert len(schema.data) == 1
        assert schema.data[0].id == requisite_trader_db.id
        assert schema.data[0].user_id == user_trader_db_with_sbp.id

    # MARK: Update
    async def test_update_requisite(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db_with_sbp: UserModel,
        requisite_trader_update_data: requisite_schemas.RequisiteUpdateSchema,
        session: AsyncSession,
    ):
        """Обновление реквизита трейдера."""

        response = await router_client.put(
            f"/requisites/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=requisite_trader_update_data.model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        schema = requisite_schemas.RequisiteGetSchema(**response.json())

        assert schema.id == requisite_trader_db.id
        assert schema.user_id == user_trader_db_with_sbp.id
        assert schema.full_name == requisite_trader_update_data.full_name

        requisite_db = await RequisiteRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert requisite_db is not None
        assert requisite_db.user_id == user_trader_db_with_sbp.id
        assert requisite_db.full_name == requisite_trader_update_data.full_name

    # MARK: Delete
    async def test_delete_requisite(
        self,
        router_client: httpx.AsyncClient,
        requisite_trader_db: RequisiteModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Удаление реквизита трейдера."""

        response = await router_client.delete(
            f"/requisites/{requisite_trader_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        requisite_db = await RequisiteRepository.get_one_or_none(
            session=session,
            id=requisite_trader_db.id,
        )

        assert requisite_db is None
