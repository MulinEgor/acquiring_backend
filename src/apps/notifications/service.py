from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.notifications import schemas
from src.apps.notifications.model import NotificationModel
from src.apps.notifications.repository import NotificationRepository
from src.lib.base.service import BaseService


class NotificationService(
    BaseService[
        NotificationModel,
        schemas.NotificationCreateSchema,
        schemas.NotificationGetSchema,
        schemas.NotificationPaginationSchema,
        schemas.NotificationListSchema,
        any,
    ],
):
    """Сервис для работы с уведомлениями."""

    repository = NotificationRepository

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        query_params: schemas.NotificationPaginationSchema,
        should_read: bool = False,
    ) -> schemas.NotificationListSchema:
        """
        Получить все уведомления.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            query_params (schemas.NotificationPaginationSchema):
                Параметры для пагинации.
            should_read (bool): Флаг для проверки, должны ли быть прочитаны уведомления.

        Returns:
            NotificationListSchema: Список уведомлений.
        """

        notifications = await super().get_all(session, query_params)

        if should_read:
            await cls.repository.update_bulk(
                session,
                notifications.data,
                {"is_read": True},
            )

        return notifications
