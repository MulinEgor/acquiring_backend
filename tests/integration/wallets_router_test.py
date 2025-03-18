"""Модуль для тестирования роутера wallets_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

import src.modules.auth.schemas as auth_schemas
import src.modules.wallets.schemas as wallet_schemas
from src.core import constants
from src.modules.wallets.models import WalletModel
from src.modules.wallets.repository import WalletRepository
from src.modules.wallets.router import wallets_router
from tests.integration.conftest import BaseTestRouter


class TestWalletsRouter(BaseTestRouter):
    """Класс для тестирования роутера wallets_router."""

    router = wallets_router

    # MARK: Create
    async def test_create_wallet(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        wallet_create_data: wallet_schemas.WalletCreateSchema,
        mocker,
    ):
        """Тест на создание кошелька."""

        mocker.patch(
            "src.modules.blockchain.services.tron_service.TronService.does_wallet_exist",
            return_value=True,
        )

        response = await router_client.post(
            "/wallets",
            json=wallet_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        data = wallet_schemas.WalletGetSchema(**response.json())

        assert data.address == wallet_create_data.address

    # MARK: Get
    async def test_get_wallet_by_address(
        self,
        router_client: httpx.AsyncClient,
        wallet_db: WalletModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Тест на получение кошелька по адресу.
        """

        response = await router_client.get(
            url=f"/wallets/{wallet_db.address}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        data = wallet_schemas.WalletGetSchema(**response.json())

        assert data.address == wallet_db.address

    async def test_get_wallets_by_admin_no_query(
        self,
        router_client: httpx.AsyncClient,
        wallet_db: WalletModel,
        session: AsyncSession,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Тест на получение списка кошельков без учета фильтрации.
        """

        response = await router_client.get(
            url="/wallets",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        wallets_data = wallet_schemas.WalletListSchema(**response.json())

        wallets_count = await WalletRepository.count(session=session)
        assert wallets_data.count == wallets_count

        # Ищем первого пользователя в БД и проверяем его данные.
        first_wallet_db = await WalletRepository.get_one_or_none(
            session=session, address=wallets_data.data[0].address
        )
        assert first_wallet_db is not None

        assert wallets_data.data[0].address == first_wallet_db.address
        assert wallets_data.data[0].id == first_wallet_db.id

    async def test_get_wallets_by_admin_query(
        self,
        router_client: httpx.AsyncClient,
        wallet_db: WalletModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Тест на получение списка кошельков с учетом учета фильтрации.
        """

        params = wallet_schemas.WalletPaginationSchema(address=wallet_db.address)

        response = await router_client.get(
            url="/wallets",
            params=params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        wallets_data = wallet_schemas.WalletListSchema(**response.json())

        assert wallets_data.data[0].address == wallet_db.address
        assert wallets_data.data[0].id == wallet_db.id

    async def test_delete_wallet_by_address(
        self,
        router_client: httpx.AsyncClient,
        wallet_db: WalletModel,
        session: AsyncSession,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """
        Тест на удаление кошелька по адресу.
        """

        response = await router_client.delete(
            url=f"/wallets/{wallet_db.address}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        wallet = await WalletRepository.get_one_or_none(
            session=session, address=wallet_db.address
        )
        assert wallet is None
