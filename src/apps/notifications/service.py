from src.apps.notifications import schemas
from src.apps.notifications.model import NotificationModel
from src.apps.notifications.repository import NotificationRepository
from src.libs.base.service import BaseService


class NotificationService(
    BaseService[
        NotificationModel,
        schemas.NotificationCreateSchema,
        schemas.NotificationGetSchema,
        schemas.NotificationPaginationSchema,
        schemas.NotificationListSchema,
        schemas.NotificationUpdateSchema,
    ],
):
    """Сервис для работы с уведомлениями."""

    repository = NotificationRepository
    not_found_exception_message = "Уведомления не найдены."
    conflict_exception_message = "Возник конфликт при создании уведомлений."
