"""Модуль для Pydanitc схем для мерчантов."""

from pydantic import BaseModel

from src.apps.transactions.model import TransactionPaymentMethodEnum


# MARK: Pay in
class MerchantPayInRequestSchema(BaseModel):
    """Схема для запроса на перевод средств для мерчанта."""

    amount: int
    payment_method: TransactionPaymentMethodEnum
    bank_name: str | None = None


class MerchantPayInResponseCardSchema(BaseModel):
    """
    Схема для ответа на запрос на перевод средств для мерчанта,
    способ оплаты - карта.
    """

    recipent_full_name: str
    card_number: str
    bank_name: str


class MerchantPayInResponseSBPSchema(BaseModel):
    """
    Схема для ответа на запрос на перевод средств для мерчанта,
    способ оплаты - сбп.
    """

    recipent_full_name: str
    phone_number: str
    bank_name: str


# MARK: Pay out
class MerchantPayOutRequestSchema(BaseModel):
    """Схема для запроса на вывод средств для мерчанта."""

    amount: int
    payment_method: TransactionPaymentMethodEnum
    requisite_id: int
    bank_name: str | None = None
