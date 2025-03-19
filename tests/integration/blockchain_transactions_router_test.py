"""Модуль для тестирования роутера blockchain_transactions_router."""

import httpx
from fastapi import status

import src.modules.auth.schemas as auth_schemas
from src.core import constants
from src.modules.blockchain import schemas as blockchain_schemas
from src.modules.blockchain.models import BlockchainTransactionModel
from src.modules.blockchain.router import blockchain_transactions_router
from tests.integration.conftest import BaseTestRouter


class TestBlockchainTransactionsRouter(BaseTestRouter):
    """Класс для тестирования роутера blockchain_transactions_router."""

    router = blockchain_transactions_router

    async def test_get_transaction_by_id(
        self,
        router_client: httpx.AsyncClient,
        blockchain_transaction_db: BlockchainTransactionModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Тест на получение транзакции по ID."""
        response = await router_client.get(
            f"/blockchain-transactions/{blockchain_transaction_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        schema = blockchain_schemas.TransactionGetSchema.model_validate(response.json())

        assert schema.id == blockchain_transaction_db.id
        assert schema.amount == blockchain_transaction_db.amount
        assert schema.status == blockchain_transaction_db.status

    async def test_get_transaction_by_id_failed(
        self,
        router_client: httpx.AsyncClient,
        blockchain_transaction_db: BlockchainTransactionModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Тест на получение транзакции по ID, которого не существует."""
        response = await router_client.get(
            f"/blockchain-transactions/{blockchain_transaction_db.id + 1}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_transactions(
        self,
        router_client: httpx.AsyncClient,
        blockchain_transaction_db: BlockchainTransactionModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Тест на получение транзакций с пагинацией."""
        query_params = blockchain_schemas.TransactionPaginationSchema(
            from_address=blockchain_transaction_db.from_address,
            max_amount=blockchain_transaction_db.amount,
            status=blockchain_transaction_db.status.value,
        )
        response = await router_client.get(
            "/blockchain-transactions",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_200_OK

        schema = blockchain_schemas.TransactionListSchema.model_validate(
            response.json()
        )

        assert schema.count == 1
        assert schema.data[0].id == blockchain_transaction_db.id
        assert schema.data[0].amount == blockchain_transaction_db.amount
        assert schema.data[0].status == blockchain_transaction_db.status

    async def test_get_transactions_failed(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        blockchain_transaction_db: BlockchainTransactionModel,
    ):
        """Тест на получение транзакций с пагинацией, для которых нет данных."""
        query_params = blockchain_schemas.TransactionPaginationSchema(
            min_amount=blockchain_transaction_db.amount + 1,
        )
        response = await router_client.get(
            "/blockchain-transactions",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
