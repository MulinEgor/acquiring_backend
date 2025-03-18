"""Модуль для Pydantic схем для трейдеров."""

from pydantic import BaseModel, Field


class RequestPayInSchema(BaseModel):
    """Схема для получения адреса кошелька, куда нужно перевести средства."""

    amount: int = Field(description="Сумма перевода в TRX")


class ConfirmPayInSchema(BaseModel):
    """Схема для подтверждения перевода средств на кошелек."""

    transaction_hash: str = Field(description="Хэш транзакции на блокчейне")


class ResponsePayInSchema(BaseModel):
    """Схема для ответа на запрос перевода средств."""

    wallet_address: str = Field(
        description="Адрес кошелька на блокчейне, куда нужно перевести средства"
    )
