"""Модуль для Pydantic схем для переводов средств."""

from pydantic import BaseModel, Field


# MARK: Pay in
class RequestPayInSchema(BaseModel):
    """Схема для получения адреса кошелька, куда нужно перевести средства."""

    amount: int = Field(description="Сумма перевода в TRX")


class ResponsePayInSchema(BaseModel):
    """Схема для ответа на запрос перевода средств."""

    wallet_address: str = Field(
        description="Адрес кошелька на блокчейне, куда нужно перевести средства"
    )


class ConfirmPayInSchema(BaseModel):
    """Схема для подтверждения перевода средств на кошелек."""

    transaction_hash: str = Field(description="Хэш транзакции на блокчейне")


# MARK: Pay out
class RequestPayOutSchema(BaseModel):
    """Схема для запроса вывода средств терминалом."""

    amount: int = Field(description="Сумма перевода в TRX")
    to_address: str = Field(description="Адрес кошелька, куда нужно перевести средства")


class ResponsePayOutSchema(BaseModel):
    """Схема для ответа на запрос вывода средств."""

    transaction_id: int = Field(description="Идентификатор транзакции")
