"""Модуль для работы с схемами кошельков."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class WalletCreateSchema(BaseModel):
    """Схема для создания кошелька."""

    address: str = Field(min_length=42, max_length=42)
    private_key: str = Field(min_length=66, max_length=66)


class WalletGetSchema(WalletCreateSchema):
    """Схема для получения кошелька."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WalletListSchema(DataListGetBaseSchema):
    """Схема для списка кошельков."""

    data: list[WalletGetSchema]


class WalletPaginationSchema(PaginationBaseSchema):
    """Схема для пагинации кошельков."""

    address: str | None = Field(
        default=None,
        min_length=42,
        max_length=42,
    )
    private_key: str | None = Field(
        default=None,
        min_length=66,
        max_length=66,
    )
