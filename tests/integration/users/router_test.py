"""Модуль для тестирования роутера users_router."""

from datetime import datetime, timedelta

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.common.routers.users_router import router as common_users_router
from src.api.user.routers.router import router as users_router
from src.apps.auth import schemas as auth_schemas
from src.apps.blockchain.model import BlockchainTransactionModel
from src.apps.blockchain.repository import BlockchainTransactionRepository
from src.apps.blockchain.schemas import TransactionStatusEnum, TransactionTypeEnum
from src.apps.blockchain.services.transaction_service import (
    BlockchainTransactionService,
)
from src.apps.users.model import UserModel
from src.apps.users.schemas import pay_schemas, user_schemas
from src.apps.wallets.model import WalletModel
from src.core import constants
from tests.conftest import faker
from tests.integration.conftest import BaseTestRouter


class TestCommonUserRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = common_users_router

    # MARK: Get
    async def test_get_current_user(
        self,
        router_client: httpx.AsyncClient,
        user_db: UserModel,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение информации о текущем пользователе."""

        response = await router_client.get(
            url="/users/me",
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = user_schemas.UserGetSchema(**response.json())

        assert data.id == user_db.id
        assert data.email == user_db.email


class TestUserRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = users_router

    # MARK: Patch, Pay in
    async def test_request_pay_in(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db_with_sbp: UserModel,
        wallet_db: WalletModel,
        mocker,
    ):
        """Запрос пополнения средств как трейдер."""

        mocker.patch(
            "src.apps.blockchain.services.tron_service.TronService.get_wallets_balances",
            return_value={
                wallet_db.address: 100,
            },
        )

        response = await router_client.patch(
            "/users/request-pay-in",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=pay_schemas.RequestPayInSchema(amount=100).model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert pay_schemas.ResponsePayInSchema.model_validate(response.json())

        assert await BlockchainTransactionService.get_pending_by_user_id(
            session=session,
            user_id=user_trader_db_with_sbp.id,
            type=TransactionTypeEnum.PAY_IN,
        )

    async def test_request_pay_in_conflict(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db_with_sbp: UserModel,
        wallet_db: WalletModel,
        mocker,
    ):
        """
        Запрос пополнения средств как трейдер,
        когда уже есть транзакция в процессе обработки.
        """

        # Создание транзакции в процессе обработки
        await self.test_request_pay_in(
            router_client=router_client,
            trader_jwt_tokens=trader_jwt_tokens,
            session=session,
            user_trader_db_with_sbp=user_trader_db_with_sbp,
            wallet_db=wallet_db,
            mocker=mocker,
        )

        response = await router_client.patch(
            "/users/request-pay-in",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=pay_schemas.RequestPayInSchema(amount=100).model_dump(),
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_confirm_pay_in(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db_with_sbp: UserModel,
        blockchain_transaction_db: BlockchainTransactionModel,
        mocker,
    ):
        """Подтверждение пополнения средств как трейдер."""

        mocker.patch(
            "src.apps.blockchain.services.tron_service.TronService.get_transaction_by_hash",
            return_value={
                "transaction_hash": "123",
                "amount": blockchain_transaction_db.amount,
                "from_address": "0" * 42,
                "to_address": blockchain_transaction_db.to_address,
                "created_at": faker.date_time(),
            },
        )

        trader_balance_before = user_trader_db_with_sbp.balance
        response = await router_client.patch(
            "/users/confirm-pay-in",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=pay_schemas.ConfirmPayInSchema(transaction_hash="123").model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        assert (
            await BlockchainTransactionRepository.get_one_or_none(
                session=session,
                user_id=user_trader_db_with_sbp.id,
            )
        ).status == TransactionStatusEnum.SUCCESS

        await session.refresh(user_trader_db_with_sbp)
        assert (
            user_trader_db_with_sbp.balance
            == trader_balance_before + blockchain_transaction_db.amount
        )

    async def test_confirm_pay_in_wrong_credentials(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db_with_sbp: UserModel,
        blockchain_transaction_db: BlockchainTransactionModel,
        mocker,
    ):
        """
        Подтверждение пополнения средств как трейдер,
        когда транзакция не соответствует ожидаемой.
        """

        mocker.patch(
            "src.apps.blockchain.services.tron_service.TronService.get_transaction_by_hash",
            return_value={
                "transaction_hash": "123",
                "amount": blockchain_transaction_db.amount - 30,
                "from_address": "0" * 42,
                "to_address": blockchain_transaction_db.to_address,
                "created_at": faker.date_time(),
            },
        )

        trader_balance_before = user_trader_db_with_sbp.balance
        response = await router_client.patch(
            "/users/confirm-pay-in",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=pay_schemas.ConfirmPayInSchema(transaction_hash="123").model_dump(),
        )

        assert response.status_code == status.HTTP_409_CONFLICT

        assert (
            await BlockchainTransactionRepository.get_one_or_none(
                session=session,
                user_id=user_trader_db_with_sbp.id,
            )
        ).status == TransactionStatusEnum.FAILED

        await session.refresh(user_trader_db_with_sbp)
        assert (
            user_trader_db_with_sbp.balance
            != trader_balance_before + blockchain_transaction_db.amount
        )

    async def test_confirm_pay_in_expired(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db_with_sbp: UserModel,
        blockchain_transaction_db: BlockchainTransactionModel,
        mocker,
    ):
        """
        Подтверждение пополнения средств как трейдер,
        когда транзакция просрочена.
        """

        blockchain_transaction_db.expires_at = datetime.now() - timedelta(
            seconds=constants.PENDING_BLOCKCHAIN_TRANSACTION_TIMEOUT + 1
        )

        mocker.patch(
            "src.apps.blockchain.services.tron_service.TronService.get_transaction_by_hash",
            return_value={
                "transaction_hash": "123",
                "amount": blockchain_transaction_db.amount,
                "from_address": "0" * 42,
                "to_address": blockchain_transaction_db.to_address,
                "created_at": faker.date_time(),
            },
        )

        trader_balance_before = user_trader_db_with_sbp.balance
        response = await router_client.patch(
            "/users/confirm-pay-in",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=pay_schemas.ConfirmPayInSchema(transaction_hash="123").model_dump(),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        assert (
            await BlockchainTransactionRepository.get_one_or_none(
                session=session,
                user_id=user_trader_db_with_sbp.id,
            )
        ).status == TransactionStatusEnum.FAILED

        await session.refresh(user_trader_db_with_sbp)
        assert (
            user_trader_db_with_sbp.balance
            != trader_balance_before + blockchain_transaction_db.amount
        )

    # MARK: Pay out
    async def test_request_pay_out(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db_with_sbp: UserModel,
        wallet_db: WalletModel,
        mocker,
    ):
        """Запрос вывода средств как трейдер."""

        user_trader_db_with_sbp.balance = 200
        await session.commit()
        amount = 100
        to_address = "0" * 42

        mocker.patch(
            "src.apps.blockchain.services.tron_service.TronService.get_wallets_balances",
            return_value={
                wallet_db.address: amount,
            },
        )

        response = await router_client.patch(
            "/users/request-pay-out",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=pay_schemas.RequestPayOutSchema(
                amount=amount,
                to_address=to_address,
            ).model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        schema = pay_schemas.ResponsePayOutSchema.model_validate(response.json())

        transaction_db = await BlockchainTransactionRepository.get_one_or_none(
            session=session,
            id=schema.transaction_id,
        )

        assert transaction_db is not None
        assert transaction_db.status == TransactionStatusEnum.PENDING
        assert transaction_db.type == TransactionTypeEnum.PAY_OUT
        assert transaction_db.amount == amount
        assert transaction_db.to_address == to_address
        assert transaction_db.from_address == wallet_db.address

    async def test_request_pay_out_not_enough_balance(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_trader_db_with_sbp: UserModel,
        wallet_db: WalletModel,
    ):
        """Запрос вывода средств как трейдер, когда недостаточно средств."""

        user_trader_db_with_sbp.balance = 100
        await session.commit()
        amount = 200
        to_address = "0" * 42

        response = await router_client.patch(
            "/users/request-pay-out",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
            json=pay_schemas.RequestPayOutSchema(
                amount=amount,
                to_address=to_address,
            ).model_dump(),
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        transactions_db = await BlockchainTransactionRepository.get_all(
            session=session,
            offset=0,
            limit=10,
        )

        assert len(transactions_db) == 0
