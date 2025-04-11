"""Модуль для Pydantic схем диспутов."""

from datetime import datetime

from pydantic import BaseModel

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class DisputeCreateSchema(BaseModel):
    """Схема для создания диспута."""

    transaction_id: int
    description: str
    image_urls: list[str]


class DisputeGetSchema(DisputeCreateSchema):
    """Схема для получения диспута."""

    id: int
    winner_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DisputeUpdateSchema(BaseModel):
    """Схема для обновления диспута."""

    accept: bool
    description: str | None = None
    image_urls: list[str] | None = None


class DisputeSupportUpdateSchema(BaseModel):
    """Схема для обновления диспута поддержкой."""

    winner_id: int | None = None


class DisputeListSchema(DataListGetBaseSchema):
    """Схема для списка диспутов."""

    data: list[DisputeGetSchema]


class DisputePaginationSchema(PaginationBaseSchema):
    """Схема для пагинации диспутов."""

    transaction_id: int | None = None
    description: str | None = None
    winner_id: int | None = None


class DisputeSupportPaginationSchema(DisputePaginationSchema):
    """Схема для пагинации диспутов поддержкой."""

    user_id: int | None = None
