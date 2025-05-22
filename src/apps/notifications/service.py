from src.apps.notifications import constants, schemas
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
    not_found_exception_message, not_found_exception_code = (
        constants.NOT_FOUND_EXCEPTION_MESSAGE,
        constants.NOT_FOUND_EXCEPTION_CODE,
    )
    conflict_exception_message, conflict_exception_code = (
        constants.CONFLICT_EXCEPTION_MESSAGE,
        constants.CONFLICT_EXCEPTION_CODE,
    )
