"""Модуль для тестирования роутера src.api.admin.routers.wallets_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.routers.wallets_router import router as wallets_router
from src.apps.auth import schemas as auth_schemas
from src.apps.wallets import schemas as wallet_schemas
from src.apps.wallets.models import WalletModel
from src.apps.wallets.repository import WalletRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestWalletsRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = wallets_router

    # MARK: Post
    async def test_create_wallet(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        wallet_create_data: wallet_schemas.WalletCreateSchema,
        mocker,
    ):
        """Создание кошелька."""

        mocker.patch(
            "src.apps.blockchain.services.tron_service.TronService.does_wallet_exist",
            return_value=True,
        )

        response = await router_client.post(
            "/wallets",
            json=wallet_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = wallet_schemas.WalletGetSchema(**response.json())

        assert schema.address == wallet_create_data.address

    # MARK: Get
    async def test_get_wallet_by_address(
        self,
        router_client: httpx.AsyncClient,
        wallet_db: WalletModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение кошелька по адресу."""

        response = await router_client.get(
            url=f"/wallets/{wallet_db.address}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = wallet_schemas.WalletGetSchema(**response.json())

        assert schema.address == wallet_db.address

    async def test_get_wallets_no_query(
        self,
        router_client: httpx.AsyncClient,
        wallet_db: WalletModel,
        session: AsyncSession,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение списка кошельков без учета фильтрации."""

        response = await router_client.get(
            url="/wallets",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        schema = wallet_schemas.WalletListSchema(**response.json())

        wallets_count = await WalletRepository.count(session=session)
        assert schema.count == wallets_count

    async def test_get_wallets_query(
        self,
        router_client: httpx.AsyncClient,
        wallet_db: WalletModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение списка кошельков с учетом фильтрации."""

        params = wallet_schemas.WalletPaginationSchema(address=wallet_db.address)

        response = await router_client.get(
            url="/wallets",
            params=params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        schema = wallet_schemas.WalletListSchema(**response.json())

        assert schema.data[0].address == wallet_db.address
        assert schema.data[0].id == wallet_db.id

    async def test_delete_wallet_by_address(
        self,
        router_client: httpx.AsyncClient,
        wallet_db: WalletModel,
        session: AsyncSession,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Удаление кошелька по адресу."""

        response = await router_client.delete(
            url=f"/wallets/{wallet_db.address}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        wallet = await WalletRepository.get_one_or_none(
            session=session, address=wallet_db.address
        )
        assert wallet is None
