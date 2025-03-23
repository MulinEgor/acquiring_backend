"""
Тесты для роутера src.api.trader.routers.transactions_router.
Роутер src.api.merchant.routers.transactions_router имеет схожий функционал,
поэтому решил не дублировать тесты.
"""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.user.routers.merchant.transactions_router import (
    router as transactions_router,
)
from src.apps.auth import schemas as auth_schemas
from src.apps.transactions import schemas as transaction_schemas
from src.apps.transactions.model import TransactionModel
from src.apps.transactions.repository import TransactionRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestMerchantTraderTransactionsRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = transactions_router

    # MARK: Get
    async def test_get_transaction(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Получение транзакции."""

        response = await router_client.get(
            f"/merchant/transactions/{transaction_db.id}",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = transaction_schemas.TransactionGetSchema(**response.json())

        transaction_db = await TransactionRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert transaction_db is not None
        assert transaction_db.merchant_id == transaction_db.merchant_id
        assert transaction_db.amount == transaction_db.amount
        assert transaction_db.type == transaction_db.type
        assert transaction_db.payment_method == transaction_db.payment_method

    async def test_get_transaction_not_mine(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение не своей транзакции."""

        response = await router_client.get(
            f"/merchant/transactions/{transaction_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_transactions_no_query(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение всех транзакций мерчанта без пагинации и фильтрации."""

        response = await router_client.get(
            "/merchant/transactions",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = transaction_schemas.TransactionListGetSchema(**response.json())

        assert len(schema.data) == 1
        assert schema.data[0].id == transaction_db.id
        assert schema.data[0].merchant_id == transaction_db.merchant_id

    async def test_get_transactions_query(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение всех транзакций с пагинацией и фильтрацией."""

        query_params = transaction_schemas.TransactionPaginationSchema(
            min_amount=transaction_db.amount - 100,
        )

        response = await router_client.get(
            "/merchant/transactions",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_200_OK

        schema = transaction_schemas.TransactionListGetSchema(**response.json())

        assert len(schema.data) == 1
        assert schema.data[0].id == transaction_db.id
        assert schema.data[0].merchant_id == transaction_db.merchant_id
