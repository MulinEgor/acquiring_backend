"""Модуль для тестирования роутера disputes_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.user.routers.support.disputes_router import router as disputes_router
from src.apps.auth import schemas as auth_schemas
from src.apps.disputes import schemas as dispute_schemas
from src.apps.disputes.model import DisputeModel, DisputeStatusEnum
from src.apps.disputes.repository import DisputeRepository
from src.apps.users.repository import UserRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestSupportDisputesRouter(BaseTestRouter):
    """Класс для тестирования роутера суппорта."""

    router = disputes_router

    async def test_update_dispute_by_support(
        self,
        router_client: httpx.AsyncClient,
        dispute_db: DisputeModel,
        dispute_support_update_data: dispute_schemas.DisputeSupportUpdateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Обновление диспута суппортом."""

        response = await router_client.put(
            url=f"/support/disputes/{dispute_db.id}",
            json=dispute_support_update_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        dispute_db = await DisputeRepository.get_one_or_none(
            session=session, id=dispute_db.id
        )
        assert dispute_db.status == DisputeStatusEnum.CLOSED

        assert dispute_db.winner_id == dispute_support_update_data.winner_id
        trader_db = await UserRepository.get_one_or_none(
            session=session, id=dispute_db.winner_id
        )
        assert trader_db.amount_frozen < dispute_db.transaction.amount
