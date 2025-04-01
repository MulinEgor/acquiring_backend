"""Модуль для Pydantic схем уведомлений."""

from datetime import datetime

from pydantic import BaseModel

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class NotificationCreateSchema(BaseModel):
    """Схема для создания уведомления."""

    user_id: int
    message: str


class NotificationReadSchema(BaseModel):
    """Схема для прочтения уведомлений."""

    notification_ids: list[int]


class NotificationGetSchema(NotificationCreateSchema):
    """Схема для получения уведомления."""

    id: int
    created_at: datetime
    updated_at: datetime
    is_read: bool

    class Config:
        from_attributes = True


class NotificationUpdateSchema(BaseModel):
    """Схема для обновления уведомления."""

    message: str | None = None
    is_read: bool | None = None


class NotificationListSchema(DataListGetBaseSchema):
    """Схема для списка уведомлений."""

    data: list[NotificationGetSchema]


class NotificationPaginationBaseSchema(PaginationBaseSchema):
    """Базовая схема для пагинации уведомлений."""

    message: str | None = None


class NotificationPaginationSchema(NotificationPaginationBaseSchema):
    """Расширенная схема для пагинации уведомлений."""

    user_id: int | None = None
