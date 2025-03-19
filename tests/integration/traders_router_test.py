"""Модуль для тестирования роутера traders_router."""

from datetime import datetime, timedelta

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

import src.modules.auth.schemas as auth_schemas
from src.core import constants
from src.modules.blockchain.models import BlockchainTransactionModel, StatusEnum
from src.modules.blockchain.repository import BlockchainTransactionRepository
from src.modules.blockchain.services.transaction_service import (
    BlockchainTransactionService,
)
from src.modules.traders import schemas as traders_schemas
from src.modules.traders.router import traders_router
from src.modules.users.models import UserModel
from src.modules.wallets.models import WalletModel
from tests.conftest import faker
from tests.integration.conftest import BaseTestRouter


class TestTradersRouter(BaseTestRouter):
    """Класс для тестирования роутера traders_router."""

    router = traders_router

    async def test_request_pay_in(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db: UserModel,
        wallet_db: WalletModel,
        mocker,
    ):
        """Тест на запрос пополнения средств как трейдер."""

        mocker.patch(
            "src.modules.blockchain.services.tron_service.TronService.get_wallets_balances",
            return_value={
                wallet_db.address: 100,
            },
        )

        response = await router_client.post(
            "/traders/request-pay-in",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=traders_schemas.RequestPayInSchema(amount=100).model_dump(),
        )

        assert response.status_code == status.HTTP_200_OK
        assert traders_schemas.ResponsePayInSchema.model_validate(response.json())

        assert (
            await BlockchainTransactionService.get_pending_by_user_id(
                session=session,
                user_id=user_trader_db.id,
            )
            is not None
        )

    async def test_request_pay_in_failed(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db: UserModel,
        wallet_db: WalletModel,
        mocker,
    ):
        """
        Тест на запрос пополнения средств как трейдер,
        когда уже есть транзакция в процессе обработки.
        """

        # Создание транзакции в процессе обработки
        await self.test_request_pay_in(
            router_client=router_client,
            trader_jwt_tokens=trader_jwt_tokens,
            session=session,
            user_trader_db=user_trader_db,
            wallet_db=wallet_db,
            mocker=mocker,
        )

        response = await router_client.post(
            "/traders/request-pay-in",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=traders_schemas.RequestPayInSchema(amount=100).model_dump(),
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_confirm_pay_in(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db: UserModel,
        blockchain_transaction_db: BlockchainTransactionModel,
        mocker,
    ):
        """Тест на подтверждение пополнения средств как трейдер."""

        mocker.patch(
            "src.modules.blockchain.services.tron_service.TronService.get_transaction_by_hash",
            return_value={
                "transaction_hash": "123",
                "amount": blockchain_transaction_db.amount,
                "from_address": "0" * 42,
                "to_address": blockchain_transaction_db.to_address,
                "created_at": faker.date_time(),
            },
        )

        trader_balance_before = user_trader_db.balance
        response = await router_client.post(
            "/traders/confirm-pay-in",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=traders_schemas.ConfirmPayInSchema(
                transaction_hash="123"
            ).model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        assert (
            await BlockchainTransactionRepository.get_one_or_none(
                session=session,
                user_id=user_trader_db.id,
            )
        ).status == StatusEnum.CONFIRMED

        await session.refresh(user_trader_db)
        assert (
            user_trader_db.balance
            == trader_balance_before + blockchain_transaction_db.amount
        )

    async def test_confirm_pay_in_wrong_credentials(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db: UserModel,
        blockchain_transaction_db: BlockchainTransactionModel,
        mocker,
    ):
        """
        Тест на подтверждение пополнения средств как трейдер,
        когда транзакция не соответствует ожидаемой.
        """

        mocker.patch(
            "src.modules.blockchain.services.tron_service.TronService.get_transaction_by_hash",
            return_value={
                "transaction_hash": "123",
                "amount": blockchain_transaction_db.amount - 30,
                "from_address": "0" * 42,
                "to_address": blockchain_transaction_db.to_address,
                "created_at": faker.date_time(),
            },
        )

        trader_balance_before = user_trader_db.balance
        response = await router_client.post(
            "/traders/confirm-pay-in",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=traders_schemas.ConfirmPayInSchema(
                transaction_hash="123"
            ).model_dump(),
        )

        assert response.status_code == status.HTTP_409_CONFLICT

        assert (
            await BlockchainTransactionRepository.get_one_or_none(
                session=session,
                user_id=user_trader_db.id,
            )
        ).status == StatusEnum.FAILED

        await session.refresh(user_trader_db)
        assert (
            user_trader_db.balance
            != trader_balance_before + blockchain_transaction_db.amount
        )

    async def test_confirm_pay_in_expired(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db: UserModel,
        blockchain_transaction_db: BlockchainTransactionModel,
        mocker,
    ):
        """
        Тест на подтверждение пополнения средств как трейдер,
        когда транзакция просрочена.
        """

        blockchain_transaction_db.expires_at = datetime.now() - timedelta(
            seconds=constants.PENDING_BLOCKCHAIN_TRANSACTION_TIMEOUT + 1
        )

        mocker.patch(
            "src.modules.blockchain.services.tron_service.TronService.get_transaction_by_hash",
            return_value={
                "transaction_hash": "123",
                "amount": blockchain_transaction_db.amount,
                "from_address": "0" * 42,
                "to_address": blockchain_transaction_db.to_address,
                "created_at": faker.date_time(),
            },
        )

        trader_balance_before = user_trader_db.balance
        response = await router_client.post(
            "/traders/confirm-pay-in",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=traders_schemas.ConfirmPayInSchema(
                transaction_hash="123"
            ).model_dump(),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        assert (
            await BlockchainTransactionRepository.get_one_or_none(
                session=session,
                user_id=user_trader_db.id,
            )
        ).status == StatusEnum.FAILED

        await session.refresh(user_trader_db)
        assert (
            user_trader_db.balance
            != trader_balance_before + blockchain_transaction_db.amount
        )
