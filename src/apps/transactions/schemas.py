"""Модуль для Pydanitc схем транзакций."""

from datetime import datetime

from pydantic import BaseModel

from src.apps.transactions.model import (
    TransactionPaymentMethodEnum,
    TransactionStatusEnum,
    TransactionTypeEnum,
)
from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class TransactionCreateSchema(BaseModel):
    """Схема для создания транзакции."""

    merchant_id: int
    amount: int
    payment_method: TransactionPaymentMethodEnum
    type: TransactionTypeEnum


class TransactionGetSchema(TransactionCreateSchema):
    """Схема для получения транзакции."""

    id: int
    status: TransactionStatusEnum
    trader_id: int | None = None
    trader_requisite_id: int | None = None
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListGetSchema(DataListGetBaseSchema):
    """Схема для списка транзакций."""

    data: list[TransactionGetSchema]


class TransactionPaginationSchema(PaginationBaseSchema):
    """Схема для пагинации транзакций для трейдера и мерчанта."""

    min_amount: int | None = None
    max_amount: int | None = None
    status: TransactionStatusEnum | None = None
    payment_method: TransactionPaymentMethodEnum | None = None
    type: TransactionTypeEnum | None = None
    requisite_id: int | None = None


class TransactionAdminPaginationSchema(TransactionPaginationSchema):
    """Схема для пагинации транзакций для админа."""

    user_id: int | None = None
    merchant_id: int | None = None
    trader_id: int | None = None


class TransactionUpdateSchema(BaseModel):
    """Схема для обновления транзакции."""

    merchant_id: int | None = None
    amount: int | None = None
    payment_method: TransactionPaymentMethodEnum | None = None
    type: TransactionTypeEnum | None = None
    trader_id: int | None = None
    requisite_id: int | None = None
    status: TransactionStatusEnum | None = None
