"""Модуль для Pydanitc схем для мерчантов."""

from pydantic import BaseModel, Field, model_validator

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


class MerchantPayInResponseSBPSchema(BaseModel):
    """
    Схема для ответа на запрос на перевод средств для мерчанта,
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


# MARK: Pay out
class MerchantPayOutRequestSchema(BaseModel):
    """Схема для запроса на вывод средств для мерчанта."""

    amount: int = Field(
        description="Сумма перевода.",
    )
    payment_method: TransactionPaymentMethodEnum = Field(
        description="Способ оплаты.",
    )
    full_name: str = Field(description="ФИО")

    phone_number: str | None = Field(defualt=None, description="Номер телефона для СБП")
    bank_name: str | None = Field(default=None, description="Название банка для СБП")

    card_number: str | None = Field(default=None, description="Номер карты")

    @model_validator(mode="after")
    def validate_model(self) -> "MerchantPayOutRequestSchema":
        """
        Кастомный валидатор, который проверят, что либо привязан СБП либо карта.

        Raises:
            ValueError: Если привязаны оба или ни одного способа оплаты.
        """

        if (
            self.payment_method == TransactionPaymentMethodEnum.CARD
            and self.card_number
            and not self.phone_number
            and not self.bank_name
        ) or (
            self.payment_method == TransactionPaymentMethodEnum.SBP
            and self.phone_number
            and self.bank_name
            and not self.card_number
        ):
            return self
        else:
            raise ValueError(
                "Необходимо привязать либо СБП, либо карту, но не оба сразу"
            )
