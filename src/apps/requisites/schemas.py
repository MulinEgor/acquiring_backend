"""Модуль для Pydanitc схем реквизитов."""

from pydantic import BaseModel, Field, model_validator

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


# MARK: Trader
class RequisiteCreateSchema(BaseModel):
    """Pydanitc схема для создания реквизитов."""

    full_name: str = Field(description="ФИО")

    phone_number: str | None = Field(default=None, description="Номер телефона для СБП")
    bank_name: str = Field(description="Название банка")
    card_number: str | None = Field(default=None, description="Номер карты")

    min_amount: int | None = Field(default=None, ge=0, description="Минимальная сумма")
    max_amount: int | None = Field(default=None, ge=0, description="Максимальная сумма")

    @model_validator(mode="after")
    def validate_model(self):
        """
        Кастомный валидатор, который проверят, что либо привязан СБП либо карта.

        Raises:
            ValueError: Если привязаны оба способа оплаты.
        """
        if (self.phone_number and not self.card_number) or (
            not self.phone_number and self.card_number
        ):
            return self
        else:
            raise ValueError(
                "Необходимо привязать либо СБП, либо карту, но не оба сразу"
            )


class RequisiteGetSchema(RequisiteCreateSchema):
    """Pydanitc схема для получения реквизитов."""

    id: int = Field(description="ID реквизитов")
    user_id: int = Field(description="ID пользователя")

    class Config:
        from_attributes = True


class RequisiteUpdateSchema(BaseModel):
    """Pydanitc схема для обновления реквизитов."""

    full_name: str | None = Field(default=None, description="ФИО")

    phone_number: str | None = Field(default=None, description="Номер телефона для СБП")
    bank_name: str | None = Field(default=None, description="Название банка для СБП")

    card_number: str | None = Field(default=None, description="Номер карты")

    min_amount: int | None = Field(default=None, ge=0, description="Минимальная сумма")
    max_amount: int | None = Field(default=None, ge=0, description="Максимальная сумма")


class RequisiteListGetSchema(DataListGetBaseSchema):
    """Pydanitc схема для получения списка реквизитов."""

    data: list[RequisiteGetSchema] = Field(description="Список реквизитов")


class RequisitePaginationSchema(PaginationBaseSchema):
    """Pydanitc схема для пагинации реквизитов."""

    full_name: str | None = Field(default=None, description="ФИО")

    phone_number: str | None = Field(default=None, description="Номер телефона для СБП")
    bank_name: str | None = Field(default=None, description="Название банка для СБП")

    card_number: str | None = Field(default=None, description="Номер карты")

    min_amount: int | None = Field(default=None, ge=0, description="Минимальная сумма")
    max_amount: int | None = Field(default=None, ge=0, description="Максимальная сумма")


# MARK: Admin
class RequisiteCreateAdminSchema(RequisiteCreateSchema):
    """Pydanitc схема для создания реквизитов админом."""

    user_id: int = Field(description="ID пользователя")


class RequisiteUpdateAdminSchema(RequisiteUpdateSchema):
    """Pydanitc схема для обновления реквизитов."""

    user_id: int | None = Field(default=None, description="ID пользователя")


class RequisitePaginationAdminSchema(RequisitePaginationSchema):
    """Pydanitc схема для пагинации реквизитов админом."""

    user_id: int | None = Field(default=None, description="ID пользователя")
