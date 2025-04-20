import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.user.routers.transactions_router import (
    router as transactions_router,
)
from src.apps.auth import schemas as auth_schemas
from src.apps.transactions import schemas as transaction_schemas
from src.apps.transactions.model import TransactionModel
from src.apps.transactions.repository import TransactionRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestTransactionsRouter(BaseTestRouter):
    router = transactions_router

    # MARK: Get
    async def test_get_transaction(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        response = await router_client.get(
            f"/transactions/{transaction_db.id}",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = transaction_schemas.TransactionGetSchema(**response.json())

        fetched_transaction_db = await TransactionRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert fetched_transaction_db is not None
        assert fetched_transaction_db.merchant_id == transaction_db.merchant_id
        assert fetched_transaction_db.amount == transaction_db.amount
        assert fetched_transaction_db.type == transaction_db.type
        assert fetched_transaction_db.payment_method == transaction_db.payment_method

    async def test_get_transaction_not_mine(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        response = await router_client.get(
            f"/transactions/{transaction_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_transactions_no_query(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        response = await router_client.get(
            "/transactions",
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
        query_params = transaction_schemas.TransactionPaginationSchema(
            min_amount=transaction_db.amount - 100,
        )

        response = await router_client.get(
            "/transactions",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_200_OK

        schema = transaction_schemas.TransactionListGetSchema(**response.json())

        assert len(schema.data) == 1
        assert schema.data[0].id == transaction_db.id
        assert schema.data[0].merchant_id == transaction_db.merchant_id
