"""Модуль для Pydantic схем диспутов."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class DisputeCreateSchema(BaseModel):
    """Схема для создания диспута."""

    transaction_id: int = Field(
        description="Идентификатор транзакции в БД",
    )
    description: str = Field(
        max_length=255,
        description="Описание диспута",
    )
    image_urls: list[str] = Field(
        description="Ссылки на изображения",
    )


class DisputeGetSchema(DisputeCreateSchema):
    """Схема для получения диспута."""

    id: int = Field(
        description="Идентификатор диспута в БД",
    )
    winner_id: int | None = Field(
        description="Идентификатор победителя в БД",
    )
    created_at: datetime = Field(
        description="Дата создания диспута",
    )
    updated_at: datetime = Field(
        description="Дата обновления диспута",
    )

    class Config:
        from_attributes = True


class DisputeUpdateSchema(BaseModel):
    """Схема для обновления диспута."""

    winner_id: int | None = Field(
        default=None,
        description="Идентификатор победителя в БД",
    )
    description: str | None = Field(
        max_length=255,
        default=None,
        description="Описание диспута",
    )
    image_urls: list[str] | None = Field(
        default=None,
        description="Ссылки на изображения",
    )


class DisputeListSchema(DataListGetBaseSchema):
    """Схема для списка диспутов."""

    data: list[DisputeGetSchema] = Field(
        description="Список диспутов",
    )


class DisputePaginationSchema(PaginationBaseSchema):
    """Схема для пагинации диспутов."""

    transaction_id: int | None = Field(
        default=None,
        description="Идентификатор транзакции в БД",
    )
    description: str | None = Field(
        default=None,
        description="Описание диспута",
    )
    winner_id: int | None = Field(
        default=None,
        description="Идентификатор победителя в БД",
    )
