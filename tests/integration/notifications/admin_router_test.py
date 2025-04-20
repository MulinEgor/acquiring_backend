import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.routers.notifications_router import router as notifications_router
from src.apps.auth import schemas as auth_schemas
from src.apps.notifications import schemas as notification_schemas
from src.apps.notifications.model import NotificationModel
from src.apps.notifications.repository import NotificationRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestNotificationsRouter(BaseTestRouter):
    router = notifications_router

    # MARK: Post
    async def test_create_notification(
        self,
        router_client: httpx.AsyncClient,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
        notification_create_data: notification_schemas.NotificationCreateSchema,
    ):
        response = await router_client.post(
            "/notifications",
            json=notification_create_data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_201_CREATED

        schema = notification_schemas.NotificationGetSchema(**response.json())

        assert schema.message == notification_create_data.message

    # MARK: Get
    async def test_get_notification_by_id(
        self,
        router_client: httpx.AsyncClient,
        notification_db: NotificationModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        response = await router_client.get(
            url=f"/notifications/{notification_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_200_OK

        schema = notification_schemas.NotificationGetSchema(**response.json())

        assert schema.message == notification_db.message

    async def test_get_notifications_no_query(
        self,
        router_client: httpx.AsyncClient,
        notification_db: NotificationModel,
        session: AsyncSession,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        response = await router_client.get(
            url="/notifications",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        schema = notification_schemas.NotificationListSchema(**response.json())

        notifications_count = await NotificationRepository.count(session=session)
        assert schema.count == notifications_count

    async def test_get_notifications_query(
        self,
        router_client: httpx.AsyncClient,
        notification_db: NotificationModel,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        params = notification_schemas.NotificationPaginationSchema(
            message=notification_db.message
        )

        response = await router_client.get(
            url="/notifications",
            params=params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        schema = notification_schemas.NotificationListSchema(**response.json())

        assert schema.data[0].message == notification_db.message
        assert schema.data[0].id == notification_db.id

    # MARK: Delete
    async def test_delete_notification_by_id(
        self,
        router_client: httpx.AsyncClient,
        notification_db: NotificationModel,
        session: AsyncSession,
        admin_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        response = await router_client.delete(
            url=f"/notifications/{notification_db.id}",
            headers={constants.AUTH_HEADER_NAME: admin_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        notification = await NotificationRepository.get_one_or_none(
            session=session, id=notification_db.id
        )
        assert notification is None
