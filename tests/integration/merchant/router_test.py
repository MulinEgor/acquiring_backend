"""Модуль для тестирования роутера src.api.merchant.routers.router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.user.routers.merchants.router import router as merchants_router
from src.apps.auth import schemas as auth_schemas
from src.apps.merchants import schemas as merchant_schemas
from src.apps.transactions.model import (
    TransactionPaymentMethodEnum,
    TransactionStatusEnum,
    TransactionTypeEnum,
)
from src.apps.transactions.repository import TransactionRepository
from src.apps.users.model import UserModel
from src.apps.users.repository import UserRepository
from src.core import constants
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
        user_trader_db_with_sbp: UserModel,
    ):
        """Запрос пополнения средств как мерчант."""

        response = await router_client.post(
            "/merchant-clients/request-pay-in",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
            json=merchant_schemas.MerchantPayInRequestSchema(
                amount=100,
                payment_method=TransactionPaymentMethodEnum.SBP,
            ).model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert merchant_schemas.MerchantPayInResponseSBPSchema.model_validate(
            response.json()
        )

        assert (
            await TransactionRepository.get_one_or_none(
                session=session,
                merchant_id=user_merchant_db.id,
            )
        ) is not None

    async def test_request_pay_in_conflict(
        self,
        router_client: httpx.AsyncClient,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_merchant_db: UserModel,
        user_trader_db_with_sbp: UserModel,
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
            user_trader_db_with_sbp=user_trader_db_with_sbp,
        )

        response = await router_client.post(
            "/merchant-clients/request-pay-in",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
            json=merchant_schemas.MerchantPayInRequestSchema(
                amount=100,
                payment_method=TransactionPaymentMethodEnum.SBP,
            ).model_dump(),
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    # MARK: Pay out
    async def test_request_pay_out(
        self,
        router_client: httpx.AsyncClient,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_merchant_db: UserModel,
        user_trader_db_with_card: UserModel,
        merchant_pay_out_create_data: merchant_schemas.MerchantPayOutRequestSchema,
    ):
        """Запрос вывода средств как мерчант."""

        user_merchant_db.balance = 200
        await session.commit()

        response = await router_client.post(
            "/merchant-clients/request-pay-out",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
            json=merchant_pay_out_create_data.model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        assert await TransactionRepository.get_one_or_none(
            session=session,
            merchant_id=user_merchant_db.id,
            type=TransactionTypeEnum.PAY_OUT,
            status=TransactionStatusEnum.PENDING,
        )
        merchant_db = await UserRepository.get_one_or_none(
            session=session,
            id=user_merchant_db.id,
        )

        assert merchant_db.amount_frozen == merchant_pay_out_create_data.amount

    async def test_request_pay_out_trader_not_found(
        self,
        router_client: httpx.AsyncClient,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_merchant_db: UserModel,
        merchant_pay_out_create_data: merchant_schemas.MerchantPayOutRequestSchema,
    ):
        """Запрос вывода средств как мерчант, когда трейдер не найден."""

        user_merchant_db.balance = 200
        await session.commit()

        response = await router_client.post(
            "/merchant-clients/request-pay-out",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
            json=merchant_pay_out_create_data.model_dump(),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

        await TransactionRepository.get_one_or_none(
            session=session,
            merchant_id=user_merchant_db.id,
            type=TransactionTypeEnum.PAY_OUT,
            status=TransactionStatusEnum.PENDING,
        ) is None
        merchant_db = await UserRepository.get_one_or_none(
            session=session,
            id=user_merchant_db.id,
        )

        assert merchant_db.amount_frozen == 0

    async def test_request_pay_out_not_enough_balance(
        self,
        router_client: httpx.AsyncClient,
        merchant_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
        user_merchant_db: UserModel,
        merchant_pay_out_create_data: merchant_schemas.MerchantPayOutRequestSchema,
    ):
        """Запрос вывода средств как мерчант, когда не хватает средств."""

        response = await router_client.post(
            "/merchant-clients/request-pay-out",
            headers={constants.AUTH_HEADER_NAME: merchant_jwt_tokens.access_token},
            json=merchant_pay_out_create_data.model_dump(),
        )

        assert response.status_code == status.HTTP_409_CONFLICT

        await TransactionRepository.get_one_or_none(
            session=session,
            merchant_id=user_merchant_db.id,
            type=TransactionTypeEnum.PAY_OUT,
            status=TransactionStatusEnum.PENDING,
        ) is None
        merchant_db = await UserRepository.get_one_or_none(
            session=session,
            id=user_merchant_db.id,
        )

        assert merchant_db.amount_frozen == 0
