"""Модуль для Pydanitc схем для мерчантов."""

from pydantic import BaseModel, Field

from src.apps.transactions.model import TransactionPaymentMethodEnum


class MerchantPayInRequestSchema(BaseModel):
    """Схема для запроса на перевод средств в мерчант."""

    amount: int = Field(
        description="Сумма перевода.",
    )
    payment_method: TransactionPaymentMethodEnum = Field(
        description="Способ оплаты.",
    )


class MerchantPayInResponseCardSchema(BaseModel):
    """
    Схема для ответа на запрос на перевод средств в мерчант,
    способ оплаты - карта.
    """

    recipent_full_name: str = Field(
        description="Имя получателя.",
    )
    card_number: str = Field(
        description="Номер карты.",
    )


class MerchantPayInResponseSbpSchema(BaseModel):
    """
    Схема для ответа на запрос на перевод средств в мерчант,
    способ оплаты - сбп.
    """

    recipent_full_name: str = Field(
        description="Имя получателя.",
    )
    bank_name: str = Field(
        description="Название банка.",
    )
    phone_number: str = Field(
        description="Номер телефона для перевода.",
    )
