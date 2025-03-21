"""Модуль для Pydanitc схем транзакций."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.apps.transactions.model import (
    TransactionPaymentMethodEnum,
    TransactionStatusEnum,
    TransactionTypeEnum,
)
from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class TransactionCreateSchema(BaseModel):
    """Схема для создания транзакции."""

    merchant_id: int = Field(description="Идентификатор мерчанта")
    amount: int = Field(description="Сумма транзакции")
    payment_method: TransactionPaymentMethodEnum = Field(description="Способ оплаты")
    type: TransactionTypeEnum = Field(description="Тип транзакции")


class TransactionGetSchema(TransactionCreateSchema):
    """Схема для получения транзакции."""

    id: int = Field(description="Идентификатор транзакции")
    status: TransactionStatusEnum = Field(description="Статус транзакции")
    trader_id: int | None = Field(default=None, description="Идентификатор трейдера")
    created_at: datetime = Field(description="Время создания транзакции")
    updated_at: datetime = Field(description="Время обновления транзакции")

    class Config:
        from_attributes = True


class TransactionListGetSchema(DataListGetBaseSchema):
    """Схема для списка транзакций."""

    data: list[TransactionGetSchema] = Field(description="Список транзакций")


class TransactionPaginationSchema(PaginationBaseSchema):
    """Схема для пагинации транзакций для трейдера и мерчанта."""

    min_amount: int | None = Field(default=None, description="Минимальная сумма")
    max_amount: int | None = Field(default=None, description="Максимальная сумма")
    status: TransactionStatusEnum | None = Field(
        default=None, description="Статус транзакции"
    )
    payment_method: TransactionPaymentMethodEnum | None = Field(
        default=None, description="Способ оплаты"
    )
    type: TransactionTypeEnum | None = Field(default=None, description="Тип транзакции")


class TransactionAdminPaginationSchema(PaginationBaseSchema):
    """Схема для пагинации транзакций для админа."""

    merchant_id: int | None = Field(default=None, description="Идентификатор мерчанта")
    min_amount: int | None = Field(default=None, description="Минимальная сумма")
    max_amount: int | None = Field(default=None, description="Максимальная сумма")
    status: TransactionStatusEnum | None = Field(
        default=None, description="Статус транзакции"
    )
    payment_method: TransactionPaymentMethodEnum | None = Field(
        default=None, description="Способ оплаты"
    )
    type: TransactionTypeEnum | None = Field(default=None, description="Тип транзакции")
    trader_id: int | None = Field(default=None, description="Идентификатор трейдера")


class TransactionUpdateSchema(BaseModel):
    """Схема для обновления транзакции."""

    merchant_id: int | None = Field(default=None, description="Идентификатор мерчанта")
    amount: int | None = Field(default=None, description="Сумма транзакции")
    payment_method: TransactionPaymentMethodEnum | None = Field(
        default=None, description="Способ оплаты"
    )
    type: TransactionTypeEnum | None = Field(default=None, description="Тип транзакции")
    trader_id: int | None = Field(default=None, description="Идентификатор трейдера")
    status: TransactionStatusEnum | None = Field(
        default=None, description="Статус транзакции"
    )
