"""Модуль для Pydantic схем транзакций на блокчейне."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.apps.blockchain.model import StatusEnum, TypeEnum
from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class TransactionCreateSchema(BaseModel):
    """Схема для создания транзакции на блокчейне."""

    user_id: int = Field(description="Идентификатор пользователя")
    to_address: str = Field(description="Адрес кошелька, куда переведена сумма")
    from_address: str | None = Field(
        default=None, description="Адрес кошелька, откуда будет переведена сумма"
    )
    amount: int = Field(description="Сумма перевода")
    type: TypeEnum = Field(description="Тип транзакции")


class TransactionUpdateSchema(BaseModel):
    """Схема для обновления транзакции на блокчейне."""

    hash: str = Field(description="Хэш транзакции")
    from_address: str = Field(description="Адрес кошелька, откуда переведена сумма")
    status: StatusEnum = Field(description="Статус транзакции")
    created_at: datetime = Field(description="Временная метка транзакции")


class TransactionGetSchema(BaseModel):
    """Схема для получения транзакции на блокчейне."""

    id: int = Field(description="Идентификатор транзакции")
    user_id: int = Field(description="Идентификатор пользователя")
    amount: int = Field(description="Сумма перевода")
    updated_at: datetime = Field(description="Временная метка обновления транзакции")
    hash: str | None = Field(default=None, description="Хэш транзакции")
    from_address: str | None = Field(
        default=None, description="Адрес кошелька, откуда переведена сумма"
    )
    status: StatusEnum = Field(description="Статус транзакции")
    created_at: datetime = Field(description="Временная метка транзакции")

    class Config:
        from_attributes = True


class TransactionListSchema(DataListGetBaseSchema):
    """Схема для списка транзакций на блокчейне."""

    data: list[TransactionGetSchema] = Field(description="Список транзакций")


class TransactionPaginationSchema(PaginationBaseSchema):
    """Схема для пагинации транзакций на блокчейне."""

    hash: str | None = Field(default=None, description="Хэш транзакции")
    from_address: str | None = Field(default=None, description="Адрес кошелька")
    to_address: str | None = Field(default=None, description="Адрес кошелька")
    min_amount: int | None = Field(
        default=None, description="Минимальная сумма транзакции", ge=0
    )
    max_amount: int | None = Field(
        default=None, description="Максимальная сумма транзакции", ge=0
    )
    type: str | None = Field(
        default=None,
        description="Тип транзакции",
        enum=[type.value for type in TypeEnum],
    )
    status: str | None = Field(
        default=None,
        description="Статус транзакции",
        enum=[status.value for status in StatusEnum],
    )
