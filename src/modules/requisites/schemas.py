"""Модуль для Pydanitc схем реквизитов."""

from pydantic import BaseModel, Field, model_validator


# MARK: Trader
class RequisiteCreateSchema(BaseModel):
    """Pydanitc схема для создания реквизитов."""

    full_name: str = Field(description="ФИО")

    phone_number: str | None = Field(defualt=None, description="Номер телефона для СБП")
    bank_name: str | None = Field(default=None, escription="Название банка для СБП")

    card_number: str | None = Field(default=None, description="Номер карты")

    min_amount: int | None = Field(default=None, ge=0, description="Минимальная сумма")
    max_amount: int | None = Field(default=None, ge=0, description="Максимальная сумма")
    max_daily_amount: int | None = Field(
        default=None, ge=0, description="Максимальная сумма в день"
    )

    @model_validator(mode="after")
    def validate_model(self) -> "RequisiteCreateSchema":
        """
        Кастомный валидатор, который проверят, что либо привязан СБП либо карта.

        Raises:
            ValueError: Если привязаны оба способа оплаты.
        """
        if self.phone_number and self.bank_name and not self.card_number:
            return self
        elif not self.phone_number and self.card_number:
            return self
        else:
            raise ValueError(
                "Необходимо привязать либо СБП, либо карту, но не оба сразу"
            )


class RequisiteGetSchema(RequisiteCreateSchema):
    """Pydanitc схема для получения реквизитов."""

    id: int = Field(description="ID реквизитов")
    user_id: int = Field(description="ID пользователя")


# MARK: Admin
class RequisiteCreateAdminSchema(RequisiteCreateSchema):
    """Pydanitc схема для создания реквизитов админом."""

    user_id: int = Field(description="ID пользователя")
