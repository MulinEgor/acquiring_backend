"""Тесты для роутера src.api.admin.routers.transactions_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.routers.transactions_router import router as transactions_router
from src.apps.auth import schemas as auth_schemas
from src.apps.transactions import schemas as transaction_schemas
from src.apps.transactions.model import TransactionModel
from src.apps.transactions.repository import TransactionRepository
from src.apps.users.model import UserModel
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestAdminTransactionsRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = transactions_router

    # MARK: Post
    async def test_create_transaction(
        self,
        router_client: httpx.AsyncClient,
        transaction_create_data: transaction_schemas.TransactionCreateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Создание транзакции."""

        response = await router_client.post(
            "/transactions",
            json=transaction_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = transaction_schemas.TransactionGetSchema(**response.json())

        transaction_db = await TransactionRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert transaction_db is not None
        assert transaction_db.merchant_id == transaction_create_data.merchant_id
        assert transaction_db.amount == transaction_create_data.amount
        assert transaction_db.type == transaction_create_data.type
        assert transaction_db.payment_method == transaction_create_data.payment_method

    async def test_create_transaction_not_authorized(
        self,
        router_client: httpx.AsyncClient,
        transaction_create_data: transaction_schemas.TransactionCreateSchema,
        trader_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Создание транзакции не авторизованным пользователем."""

        response = await router_client.post(
            "/transactions",
            json=transaction_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: trader_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

        transactions_db = await TransactionRepository.get_all(session=session)
        assert len(transactions_db) == 0

    # MARK: Get
    async def test_get_transaction(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Получение транзакции."""

        response = await router_client.get(
            f"/transactions/{transaction_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
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

    async def test_get_transactions_no_query(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        user_trader_db_with_sbp: UserModel,
    ):
        """Получение всех транзакций администратором без пагинации и фильтрации."""

        response = await router_client.get(
            "/transactions",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
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
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        user_merchant_db: UserModel,
    ):
        """Получение всех транзакций с пагинацией и фильтрацией."""

        query_params = transaction_schemas.TransactionAdminPaginationSchema(
            merchant_id=user_merchant_db.id,
        )

        response = await router_client.get(
            "/transactions",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
            params=query_params.model_dump(exclude_none=True),
        )

        assert response.status_code == status.HTTP_200_OK

        schema = transaction_schemas.TransactionListGetSchema(**response.json())

        assert len(schema.data) == 1
        assert schema.data[0].id == transaction_db.id
        assert schema.data[0].merchant_id == transaction_db.merchant_id

    # MARK: Put
    async def test_update_requisite(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        transaction_update_data: transaction_schemas.TransactionUpdateSchema,
        session: AsyncSession,
    ):
        """Обновление транзакции."""

        response = await router_client.put(
            f"/transactions/{transaction_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
            json=transaction_update_data.model_dump(),
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        schema = transaction_schemas.TransactionGetSchema(**response.json())

        assert schema.id == transaction_db.id
        assert schema.trader_id == transaction_update_data.trader_id

        transaction = await TransactionRepository.get_one_or_none(
            session=session,
            id=schema.id,
        )

        assert transaction is not None
        assert transaction.trader_id == transaction_update_data.trader_id

    # MARK: Delete
    async def test_delete_requisite(
        self,
        router_client: httpx.AsyncClient,
        transaction_db: TransactionModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Удаление транзакции."""

        response = await router_client.delete(
            f"/transactions/{transaction_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        transactions_db = await TransactionRepository.get_all(session=session)
        assert len(transactions_db) == 0
