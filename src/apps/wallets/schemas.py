from datetime import datetime

from pydantic import BaseModel, Field

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class WalletCreateSchema(BaseModel):
    address: str = Field(min_length=42, max_length=42)
    private_key: str = Field(min_length=66, max_length=66)


class WalletGetSchema(WalletCreateSchema):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WalletListSchema(DataListGetBaseSchema):
    data: list[WalletGetSchema]


class WalletPaginationSchema(PaginationBaseSchema):
    address: str | None = Field(
        default=None,
        min_length=42,
        max_length=42,
    )
    private_key: str | None = Field(
        default=None,
        min_length=66,
        max_length=66,
    )
