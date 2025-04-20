import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.routers.sms_regex_router import router as sms_regex_router
from src.apps.auth import schemas as auth_schemas
from src.apps.sms_regex import schemas
from src.apps.sms_regex.model import SmsRegexModel
from src.apps.sms_regex.repository import SmsRegexRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestSmsRegexRouter(BaseTestRouter):
    router = sms_regex_router

    # MARK: Post
    async def test_create_sms_regex(
        self,
        router_client: httpx.AsyncClient,
        sms_regex_create_data: schemas.SmsRegexCreateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        response = await router_client.post(
            "/sms-regex",
            json=sms_regex_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = schemas.SmsRegexGetSchema(**response.json())
        assert schema.sender == sms_regex_create_data.sender

        sms_regex_db = await SmsRegexRepository.get_one_or_none(
            session=session,
            sender=sms_regex_create_data.sender,
        )
        assert sms_regex_db is not None
        assert sms_regex_db.sender == sms_regex_create_data.sender

    # MARK: Get
    async def test_get_sms_regex_by_id(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        sms_regex_db: SmsRegexModel,
    ):
        response = await router_client.get(
            f"/sms-regex/{sms_regex_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = schemas.SmsRegexGetSchema(**response.json())
        assert schema.id == sms_regex_db.id
        assert schema.sender == sms_regex_db.sender

    async def test_get_all_sms_regex_no_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        sms_regex_db: SmsRegexModel,
    ):
        response = await router_client.get(
            "/sms-regex",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = schemas.SmsRegexListGetSchema(**response.json())

        assert schema.count >= 1

    async def test_get_all_sms_regex_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        sms_regex_db: SmsRegexModel,
    ):
        query_params = schemas.SmsRegexPaginationSchema(sender=sms_regex_db.sender[:2])

        response = await router_client.get(
            "/sms-regex",
            params=query_params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = schemas.SmsRegexListGetSchema(**response.json())

        assert schema.count == 1
        assert schema.data[0].id == sms_regex_db.id
        assert schema.data[0].sender == sms_regex_db.sender

    # MARK: Put
    async def test_update_sms_regex(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        sms_regex_db: SmsRegexModel,
        sms_regex_update_data: schemas.SmsRegexUpdateSchema,
    ):
        response = await router_client.put(
            f"/sms-regex/{sms_regex_db.id}",
            json=sms_regex_update_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        schema = schemas.SmsRegexGetSchema(**response.json())
        assert schema.id == sms_regex_db.id
        assert schema.regex == sms_regex_update_data.regex

    # MARK: Delete
    async def test_delete_sms_regex(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        sms_regex_db: SmsRegexModel,
        session: AsyncSession,
    ):
        response = await router_client.delete(
            f"/sms-regex/{sms_regex_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        deleted_sms_regex_db = await SmsRegexRepository.get_one_or_none(
            session=session,
            sender=sms_regex_db.sender,
        )
        assert deleted_sms_regex_db is None
