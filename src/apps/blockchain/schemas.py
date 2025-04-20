from datetime import datetime

from pydantic import BaseModel

from src.apps.transactions.model import TransactionStatusEnum, TransactionTypeEnum
from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class TransactionCreateSchema(BaseModel):
    """Схема для создания транзакции на блокчейне."""

    user_id: int
    to_address: str
    from_address: str | None = None
    amount: int
    type: TransactionTypeEnum


class TransactionUpdateSchema(BaseModel):
    """Схема для обновления транзакции на блокчейне."""

    hash: str
    from_address: str
    status: TransactionStatusEnum
    created_at: datetime


class TransactionGetSchema(BaseModel):
    """Схема для получения транзакции на блокчейне."""

    id: int
    user_id: int
    amount: int
    updated_at: datetime
    hash: str | None = None
    from_address: str | None = None
    status: TransactionStatusEnum
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionListSchema(DataListGetBaseSchema):
    """Схема для списка транзакций на блокчейне."""

    data: list[TransactionGetSchema]


class TransactionPaginationSchema(PaginationBaseSchema):
    """Схема для пагинации транзакций на блокчейне."""

    hash: str | None = None
    from_address: str | None = None
    to_address: str | None = None
    min_amount: int | None = None
    max_amount: int | None = None
    type: str | None = None
    status: str | None = None
