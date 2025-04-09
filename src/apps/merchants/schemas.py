"""Модуль для Pydanitc схем для мерчантов."""

from pydantic import BaseModel, Field

from src.apps.transactions.model import TransactionPaymentMethodEnum


# MARK: Pay in
class MerchantPayInRequestSchema(BaseModel):
    """Схема для запроса на перевод средств для мерчанта."""

    amount: int = Field(
        description="Сумма перевода.",
    )
    payment_method: TransactionPaymentMethodEnum = Field(
        description="Способ оплаты.",
    )
    bank_name: str | None = Field(
        default=None,
        description="Название банка.",
    )


class MerchantPayInResponseCardSchema(BaseModel):
    """
    Схема для ответа на запрос на перевод средств для мерчанта,
    способ оплаты - карта.
    """

    recipent_full_name: str = Field(
        description="Имя получателя.",
    )
    card_number: str = Field(
        description="Номер карты.",
    )
    bank_name: str = Field(
        description="Название банка.",
    )


class MerchantPayInResponseSBPSchema(BaseModel):
    """
    Схема для ответа на запрос на перевод средств для мерчанта,
    способ оплаты - сбп.
    """

    recipent_full_name: str = Field(
        description="Имя получателя.",
    )
    phone_number: str = Field(
        description="Номер телефона для перевода.",
    )
    bank_name: str = Field(
        description="Название банка.",
    )


# MARK: Pay out
class MerchantPayOutRequestSchema(BaseModel):
    """Схема для запроса на вывод средств для мерчанта."""

    amount: int = Field(
        description="Сумма перевода.",
    )
    payment_method: TransactionPaymentMethodEnum = Field(
        description="Способ оплаты.",
    )
    requisite_id: int = Field(
        description="ID реквизита.",
    )
