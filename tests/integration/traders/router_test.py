"""Модуль для тестирования роутера src.api.trader.routers.router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.user.routers.traders.router import router as traders_router
from src.apps.auth import schemas as auth_schemas
from src.apps.transactions.model import (
    TransactionModel,
    TransactionStatusEnum,
)
from src.apps.transactions.repository import TransactionRepository
from src.apps.users.model import UserModel
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestTradersRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = traders_router

    # MARK: Start/stop working
    async def test_start_working(
        self,
        router_client: httpx.AsyncClient,
        session: AsyncSession,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
    ):
        """Начать работу как трейдер, буучи уже активным."""

        response = await router_client.patch(
            "/traders/start",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_409_CONFLICT

        await session.refresh(user_trader_db)
        assert user_trader_db.is_active is True

    async def test_start_working_not_active(
        self,
        router_client: httpx.AsyncClient,
        session: AsyncSession,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db: UserModel,
    ):
        """Начать работу как трейдер, буучи не активным."""

        user_trader_db.is_active = False
        await session.commit()

        response = await router_client.patch(
            "/traders/start",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        await session.refresh(user_trader_db)
        assert user_trader_db.is_active is True

    # MARK: Confirm merchant pay in
    async def test_confirm_merchant_pay_in(
        self,
        router_client: httpx.AsyncClient,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        transaction_merchant_pending_pay_in_db: TransactionModel,
        user_trader_db: UserModel,
        user_merchant_db: UserModel,
    ):
        """Подтверждение пополнения средств мерчантом от трейдера."""

        user_trader_balance_before = user_trader_db.balance

        user_trader_db.amount_frozen = transaction_merchant_pending_pay_in_db.amount
        await session.commit()

        response = await router_client.patch(
            f"/traders/confirm-merchant-pay-in/{transaction_merchant_pending_pay_in_db.id}",
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        assert (
            await TransactionRepository.get_one_or_none(
                session=session,
                id=transaction_merchant_pending_pay_in_db.id,
            )
        ) is not None

        await session.refresh(user_trader_db)
        await session.refresh(user_merchant_db)
        assert (
            user_trader_db.balance
            == user_trader_balance_before
            - transaction_merchant_pending_pay_in_db.amount
            + transaction_merchant_pending_pay_in_db.amount
            * constants.TRADER_COMMISSION
        )
        assert (
            user_merchant_db.balance
            == transaction_merchant_pending_pay_in_db.amount
            - transaction_merchant_pending_pay_in_db.amount
            * constants.MERCHANT_COMMISSION
        )

        assert (
            transaction_merchant_pending_pay_in_db.status
            == TransactionStatusEnum.SUCCESS
        )
