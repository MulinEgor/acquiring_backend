"""Модуль для тестирования роутера src.api.admin.routers.disputes_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.routers.disputes_router import router as disputes_router
from src.apps.auth import schemas as auth_schemas
from src.apps.disputes import schemas as dispute_schemas
from src.apps.disputes.model import DisputeModel
from src.apps.disputes.repository import DisputeRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestDisputesRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = disputes_router

    # MARK: Post
    async def test_create_dispute(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        dispute_create_data: dispute_schemas.DisputeCreateSchema,
    ):
        """Создание диспута."""

        response = await router_client.post(
            "/disputes",
            json=dispute_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = dispute_schemas.DisputeGetSchema(**response.json())

        assert schema.transaction_id == dispute_create_data.transaction_id

    # MARK: Get
    async def test_get_dispute_by_id(
        self,
        router_client: httpx.AsyncClient,
        dispute_db: DisputeModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение диспута по ID."""

        response = await router_client.get(
            url=f"/disputes/{dispute_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = dispute_schemas.DisputeGetSchema(**response.json())

        assert schema.transaction_id == dispute_db.transaction_id

    async def test_get_disputes_no_query(
        self,
        router_client: httpx.AsyncClient,
        dispute_db: DisputeModel,
        session: AsyncSession,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение списка диспутов без учета фильтрации."""

        response = await router_client.get(
            url="/disputes",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        schema = dispute_schemas.DisputeListSchema(**response.json())

        disputes_count = await DisputeRepository.count(session=session)
        assert schema.count == disputes_count

    async def test_get_disputes_query(
        self,
        router_client: httpx.AsyncClient,
        dispute_db: DisputeModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение списка диспутов с учетом фильтрации."""

        params = dispute_schemas.DisputePaginationSchema(
            transaction_id=dispute_db.transaction_id
        )

        response = await router_client.get(
            url="/disputes",
            params=params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        schema = dispute_schemas.DisputeListSchema(**response.json())

        assert schema.data[0].transaction_id == dispute_db.transaction_id
        assert schema.data[0].id == dispute_db.id

    # MARK: Update
    async def test_update_dispute_by_id(
        self,
        router_client: httpx.AsyncClient,
        dispute_db: DisputeModel,
        dispute_update_data: dispute_schemas.DisputeUpdateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Обновление диспута по ID."""

        response = await router_client.put(
            url=f"/disputes/{dispute_db.id}",
            json=dispute_update_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        schema = dispute_schemas.DisputeGetSchema(**response.json())

        assert schema.winner_id == dispute_update_data.winner_id
        assert schema.description == dispute_update_data.description

        dispute_db = await DisputeRepository.get_one_or_none(
            session=session, id=dispute_db.id
        )

        assert dispute_db.winner_id == dispute_update_data.winner_id
        assert dispute_db.description == dispute_update_data.description

    # MARK: Delete
    async def test_delete_dispute_by_id(
        self,
        router_client: httpx.AsyncClient,
        dispute_db: DisputeModel,
        session: AsyncSession,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Удаление диспута по ID."""

        response = await router_client.delete(
            url=f"/disputes/{dispute_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        dispute = await DisputeRepository.get_one_or_none(
            session=session, id=dispute_db.id
        )
        assert dispute is None
