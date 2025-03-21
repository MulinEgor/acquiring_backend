"""Модуль для тестирования src.api.common.routers.blockchain_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.common.routers.blockchain_router import (
    router as blockchain_transactions_router,
)
from src.apps.auth import schemas as auth_schemas
from src.apps.blockchain import schemas as blockchain_schemas
from src.apps.blockchain.models import BlockchainTransactionModel, StatusEnum
from src.apps.blockchain.repository import BlockchainTransactionRepository
from src.apps.users.models import UserModel
from src.apps.wallets.models import WalletModel
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestBlockchainTransactionsRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = blockchain_transactions_router

    # MARK: Get
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
        session: AsyncSession,
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

    async def test_get_transactions_failed(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        blockchain_transaction_db: BlockchainTransactionModel,
    ):
        """
        Тест на получение транзакций с пагинацией,
        для которых нет подходящих транзакций.
        """

        query_params = blockchain_schemas.TransactionPaginationSchema(
            min_amount=blockchain_transaction_db.amount + 1,
        )
        response = await router_client.get(
            "/blockchain-transactions",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    # MARK: Patch
    async def test_confirm_transaction(
        self,
        router_client: httpx.AsyncClient,
        blockchain_transaction_pay_out_db: BlockchainTransactionModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
        wallet_db: WalletModel,
        session: AsyncSession,
        mocker,
    ):
        """Тест на подтверждение транзакции."""

        hash = "0x123"
        trader_balance_before = user_trader_db.balance

        mocker.patch(
            "src.apps.blockchain.services.tron_service.TronService.create_and_sign_transaction",
            return_value=hash,
        )

        response = await router_client.patch(
            f"/blockchain-transactions/{blockchain_transaction_pay_out_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        transaction_db = await BlockchainTransactionRepository.get_one_or_none(
            session=session,
            id=blockchain_transaction_pay_out_db.id,
        )

        assert transaction_db is not None
        assert transaction_db.status == StatusEnum.CONFIRMED

        await session.refresh(user_trader_db)
        assert user_trader_db.balance == trader_balance_before - transaction_db.amount

    async def test_confirm_transaction_with_wrong_status(
        self,
        router_client: httpx.AsyncClient,
        blockchain_transaction_db: BlockchainTransactionModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
        session: AsyncSession,
        mocker,
    ):
        """Тест на подтверждение транзакции с неверным статусом."""

        hash = "0x123"
        trader_balance_before = user_trader_db.balance

        mocker.patch(
            "src.apps.blockchain.services.tron_service.TronService.create_and_sign_transaction",
            return_value=hash,
        )

        response = await router_client.patch(
            f"/blockchain-transactions/{blockchain_transaction_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        transaction_db = await BlockchainTransactionRepository.get_one_or_none(
            session=session,
            id=blockchain_transaction_db.id,
        )

        assert transaction_db is not None
        assert transaction_db.status == StatusEnum.PENDING

        await session.refresh(user_trader_db)
        assert user_trader_db.balance == trader_balance_before
