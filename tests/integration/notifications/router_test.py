"""Модуль для тестирования роутера notifications_router."""

import httpx
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.user.routers.notifications_router import (
    router as notifications_router,
)
from src.apps.auth import schemas as auth_schemas
from src.apps.notifications import schemas as notification_schemas
from src.apps.notifications.model import NotificationModel
from src.apps.notifications.repository import NotificationRepository
from src.core import constants
from tests.integration.conftest import BaseTestRouter


class TestNotificationsRouter(BaseTestRouter):
    """Класс для тестирования роутера."""

    router = notifications_router

    # MARK: Get
    async def test_get_notifications_no_query(
        self,
        router_client: httpx.AsyncClient,
        notification_db: NotificationModel,
        session: AsyncSession,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение списка уведомлений без учета фильтрации."""

        response = await router_client.get(
            url="/notifications",
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        schema = notification_schemas.NotificationListSchema(**response.json())

        notifications_count = await NotificationRepository.count(session=session)
        assert schema.count == notifications_count

    async def test_get_notifications_query(
        self,
        router_client: httpx.AsyncClient,
        notification_db: NotificationModel,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
    ):
        """Получение списка уведомлений с учетом фильтрации."""

        params = notification_schemas.NotificationPaginationSchema(
            message=notification_db.message
        )

        response = await router_client.get(
            url="/notifications",
            params=params.model_dump(exclude_unset=True),
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )
        assert response.status_code == status.HTTP_200_OK

        schema = notification_schemas.NotificationListSchema(**response.json())

        assert schema.data[0].message == notification_db.message
        assert schema.data[0].id == notification_db.id

    # MARK: Patch
    async def test_read_notifications(
        self,
        router_client: httpx.AsyncClient,
        notification_db: NotificationModel,
        user_jwt_tokens: auth_schemas.JWTGetSchema,
        session: AsyncSession,
    ):
        """Прочитать все уведомления."""

        assert not notification_db.is_read

        data = notification_schemas.NotificationReadSchema(
            notification_ids=[notification_db.id],
        )

        response = await router_client.patch(
            url="/notifications",
            json=data.model_dump(),
            headers={constants.AUTH_HEADER_NAME: user_jwt_tokens.access_token},
        )

        assert response.status_code == status.HTTP_202_ACCEPTED

        notification = await NotificationRepository.get_one_or_none(
            session=session, id=notification_db.id
        )

        assert notification.is_read
