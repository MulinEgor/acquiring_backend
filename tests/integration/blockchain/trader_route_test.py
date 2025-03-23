"""Модуль для тестирования src.api.trader.routers.blockchain_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.user.routers.trader.blockchain_router import (
    router as blockchain_transactions_router,
)
from src.apps.auth import schemas as auth_schemas
from src.apps.blockchain import schemas as blockchain_schemas
from src.apps.blockchain.model import BlockchainTransactionModel
from src.apps.blockchain.repository import BlockchainTransactionRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestMerchantBlockchainTransactionsRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = blockchain_transactions_router

    # MARK: Get
    async def test_get_trader_blockchain_transaction_by_id(
        self,
        router_client: httpx.AsyncClient,
        blockchain_transaction_db: BlockchainTransactionModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Тест на получение транзакции по ID."""

        response = await router_client.get(
            f"/traders/blockchain-transactions/{blockchain_transaction_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        schema = blockchain_schemas.TransactionGetSchema.model_validate(response.json())

        assert schema.id == blockchain_transaction_db.id

    async def test_get_trader_blockchain_transaction_by_id_failed(
        self,
        router_client: httpx.AsyncClient,
        blockchain_transaction_db: BlockchainTransactionModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Тест на получение транзакции по ID, которого не существует."""

        response = await router_client.get(
            f"/traders/blockchain-transactions/{blockchain_transaction_db.id + 1}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_trader_blockchain_transactions(
        self,
        router_client: httpx.AsyncClient,
        blockchain_transaction_db: BlockchainTransactionModel,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """
        Тест на получение транзакций для текущего пользователя,
        для которого есть транзакции.
        """

        query_params = blockchain_schemas.TransactionPaginationSchema(
            from_address=blockchain_transaction_db.from_address,
            max_amount=blockchain_transaction_db.amount,
            status=blockchain_transaction_db.status.value,
        )
        response = await router_client.get(
            "/traders/blockchain-transactions",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_200_OK

        schema = blockchain_schemas.TransactionListSchema.model_validate(
            response.json()
        )

        assert schema.count == 1

        transactions_db = await BlockchainTransactionRepository.get_all(
            session=session,
            offset=0,
            limit=1,
        )

        assert len(transactions_db) == 1
        assert transactions_db[0].id == blockchain_transaction_db.id
        assert transactions_db[0].id == schema.data[0].id

    async def test_get_my_transactions_failed(
        self,
        router_client: httpx.AsyncClient,
        blockchain_transaction_db: BlockchainTransactionModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Тест на получение всех транзакций для текущего пользователя,
        которому не принадлежат никакие транзакции.
        """

        query_params = blockchain_schemas.TransactionPaginationSchema(
            from_address=blockchain_transaction_db.from_address,
            max_amount=blockchain_transaction_db.amount,
            status=blockchain_transaction_db.status.value,
        )
        response = await router_client.get(
            "/traders/blockchain-transactions",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
