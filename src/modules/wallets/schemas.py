"""Модуль для работы с схемами кошельков."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.core.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class WalletCreateSchema(BaseModel):
    """Схема для создания кошелька."""

    address: str = Field(
        min_length=42,
        max_length=42,
        description="Адрес кошелька на блокчейне",
    )
    private_key: str = Field(
        min_length=66,
        max_length=66,
        description="Приватный ключ кошелька",
    )


class WalletGetSchema(WalletCreateSchema):
    """Схема для получения кошелька."""

    id: int = Field(
        description="Идентификатор кошелька в БД",
    )
    created_at: datetime = Field(
        description="Дата создания кошелька",
    )
    updated_at: datetime = Field(
        description="Дата обновления кошелька",
    )

    class Config:
        from_attributes = True


class WalletListSchema(DataListGetBaseSchema):
    """Схема для списка кошельков."""

    data: list[WalletGetSchema] = Field(
        description="Список кошельков",
    )


class WalletPaginationSchema(PaginationBaseSchema):
    """Схема для пагинации кошельков."""

    address: str | None = Field(
        min_length=42,
        max_length=42,
        default=None,
        description="Адрес кошелька",
    )
    private_key: str | None = Field(
        min_length=66,
        max_length=66,
        default=None,
        description="Приватный ключ кошелька",
    )
