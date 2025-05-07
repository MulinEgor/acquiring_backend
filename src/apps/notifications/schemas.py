from datetime import datetime

from pydantic import BaseModel

from src.libs.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class NotificationCreateSchema(BaseModel):
    user_id: int
    message: str


class NotificationReadSchema(BaseModel):
    notification_ids: list[int]


class NotificationGetSchema(NotificationCreateSchema):
    id: int
    is_read: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationUpdateSchema(BaseModel):
    message: str | None = None
    is_read: bool | None = None


class NotificationListSchema(DataListGetBaseSchema):
    data: list[NotificationGetSchema]


class NotificationPaginationBaseSchema(PaginationBaseSchema):
    message: str | None = None


class NotificationPaginationSchema(NotificationPaginationBaseSchema):
    user_id: int | None = None
