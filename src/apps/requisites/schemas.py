from pydantic import BaseModel, Field, model_validator

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


# MARK: Trader
class RequisiteCreateSchema(BaseModel):
    priority: int = 0
    full_name: str

    phone_number: str | None = None
    bank_name: str
    card_number: str | None = None

    min_amount: int | None = Field(default=None, ge=0)
    max_amount: int | None = Field(default=None, ge=0)

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
    id: int
    user_id: int

    class Config:
        from_attributes = True


class RequisiteUpdateSchema(BaseModel):
    priority: int | None = None
    full_name: str | None = None

    phone_number: str | None = None
    bank_name: str | None = None

    card_number: str | None = None

    min_amount: int | None = Field(default=None, ge=0)
    max_amount: int | None = Field(default=None, ge=0)


class RequisiteListGetSchema(DataListGetBaseSchema):
    data: list[RequisiteGetSchema]


class RequisitePaginationSchema(PaginationBaseSchema):
    priority: int | None = None
    full_name: str | None = None

    phone_number: str | None = None
    bank_name: str | None = None

    card_number: str | None = None

    min_amount: int | None = Field(default=None, ge=0)
    max_amount: int | None = Field(default=None, ge=0)


# MARK: Admin
class RequisiteCreateAdminSchema(RequisiteCreateSchema):
    user_id: int


class RequisiteUpdateAdminSchema(RequisiteUpdateSchema):
    user_id: int | None = None


class RequisitePaginationAdminSchema(RequisitePaginationSchema):
    user_id: int | None = None
