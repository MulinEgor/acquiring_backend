"""Модуль для тестирования роутера src.api.merchant.routers.router."""

import httpx
import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.merchant.routers.router import router as merchants_router
from src.apps.auth import schemas as auth_schemas
from src.apps.merchant import schemas as merchants_schemas
from src.apps.transactions.model import (
    TransactionPaymentMethodEnum,
    TransactionTypeEnum,
)
from src.apps.transactions.service import TransactionService
from src.apps.users.model import UserModel
from src.core import constants, exceptions
from tests.integration.conftest import BaseTestRouter


class TestMerchantsRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = merchants_router

    # MARK: Pay in
    async def test_request_pay_in(
        self,
        router_client: httpx.AsyncClient,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_merchant_db: UserModel,
        user_trader_db: UserModel,
    ):
        """Запрос пополнения средств как мерчант."""

        response = await router_client.post(
            "/merchant/request-pay-in",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
            json=merchants_schemas.MerchantPayInRequestSchema(
                amount=100,
                payment_method=TransactionPaymentMethodEnum.SBP,
            ).model_dump(),
        )

        assert response.status_code == status.HTTP_200_OK
        assert merchants_schemas.MerchantPayInResponseSbpSchema.model_validate(
            response.json()
        )

        await TransactionService.get_pending_by_user_id(
            session=session,
            user_id=user_merchant_db.id,
            type=TransactionTypeEnum.PAY_IN,
            role="merchant",
        )

    async def test_request_pay_in_conflict(
        self,
        router_client: httpx.AsyncClient,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_merchant_db: UserModel,
        user_trader_db: UserModel,
    ):
        """
        Запрос пополнения средств как мерчант,
        когда уже есть транзакция в процессе обработки.
        """

        # Создание транзакции в процессе обработки
        await self.test_request_pay_in(
            router_client=router_client,
            merchant_jwt_tokens=merchant_jwt_tokens,
            session=session,
            user_merchant_db=user_merchant_db,
            user_trader_db=user_trader_db,
        )

        response = await router_client.post(
            "/merchant/request-pay-in",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
            json=merchants_schemas.MerchantPayInRequestSchema(
                amount=100,
                payment_method=TransactionPaymentMethodEnum.SBP,
            ).model_dump(),
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_request_pay_in_payment_method_not_found(
        self,
        router_client: httpx.AsyncClient,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_merchant_db: UserModel,
        user_trader_db: UserModel,
    ):
        """
        Запрос пополнения средств как мерчант,
        когда нету трейдеров с таким способом оплаты.
        """

        response = await router_client.post(
            "/merchant/request-pay-in",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
            json=merchants_schemas.MerchantPayInRequestSchema(
                amount=100,
                payment_method=TransactionPaymentMethodEnum.CARD,
            ).model_dump(),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        with pytest.raises(exceptions.NotFoundException):
            await TransactionService.get_pending_by_user_id(
                session=session,
                user_id=user_merchant_db.id,
                type=TransactionTypeEnum.PAY_IN,
                role="merchant",
            )
