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
