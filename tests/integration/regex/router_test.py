import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.routers.regex_router import router as regex_router
from src.apps.auth import schemas as auth_schemas
from src.apps.regex import schemas
from src.apps.regex.model import RegexModel
from src.apps.regex.repository import RegexRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestRegexRouter(BaseTestRouter):
    router = regex_router

    # MARK: Post
    async def test_create_regex(
        self,
        router_client: httpx.AsyncClient,
        regex_create_data: schemas.RegexCreateSchema,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        response = await router_client.post(
            "/regex",
            json={
                **regex_create_data.model_dump(exclude={"type"}),
                "type": regex_create_data.type.value,
            },
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = schemas.RegexGetSchema(**response.json())
        assert schema.sender == regex_create_data.sender

        regex_db = await RegexRepository.get_one_or_none(
            session=session,
            sender=regex_create_data.sender,
        )
        assert regex_db is not None
        assert regex_db.sender == regex_create_data.sender

    # MARK: Get
    async def test_get_regex_by_id(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        regex_db: RegexModel,
    ):
        response = await router_client.get(
            f"/regex/{regex_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = schemas.RegexGetSchema(**response.json())
        assert schema.id == regex_db.id
        assert schema.sender == regex_db.sender

    async def test_get_all_regex_no_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        regex_db: RegexModel,
    ):
        response = await router_client.get(
            "/regex",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = schemas.RegexListGetSchema(**response.json())

        assert schema.count >= 1

    async def test_get_all_regex_query(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        regex_db: RegexModel,
    ):
        query_params = schemas.RegexPaginationSchema(sender=regex_db.sender[:2])

        response = await router_client.get(
            "/regex",
            params=query_params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = schemas.RegexListGetSchema(**response.json())

        assert schema.count == 1
        assert schema.data[0].id == regex_db.id
        assert schema.data[0].sender == regex_db.sender

    # MARK: Put
    async def test_update_regex(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        regex_db: RegexModel,
        regex_update_data: schemas.RegexUpdateSchema,
    ):
        response = await router_client.put(
            f"/regex/{regex_db.id}",
            json=regex_update_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        schema = schemas.RegexGetSchema(**response.json())
        assert schema.id == regex_db.id
        assert schema.regex == regex_update_data.regex

    # MARK: Delete
    async def test_delete_regex(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        regex_db: RegexModel,
        session: AsyncSession,
    ):
        response = await router_client.delete(
            f"/regex/{regex_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        deleted_regex_db = await RegexRepository.get_one_or_none(
            session=session,
            sender=regex_db.sender,
        )
        assert deleted_regex_db is None
