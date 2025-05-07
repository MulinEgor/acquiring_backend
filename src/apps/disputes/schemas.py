from datetime import datetime

from pydantic import BaseModel

from src.libs.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class DisputeCreateSchema(BaseModel):
    transaction_id: int
    description: str
    image_urls: list[str]


class DisputeGetSchema(DisputeCreateSchema):
    id: int
    winner_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DisputeUpdateSchema(BaseModel):
    accept: bool
    description: str | None = None
    image_urls: list[str] | None = None


class DisputeSupportUpdateSchema(BaseModel):
    winner_id: int | None = None


class DisputeListSchema(DataListGetBaseSchema):
    data: list[DisputeGetSchema]


class DisputePaginationSchema(PaginationBaseSchema):
    transaction_id: int | None = None
    description: str | None = None
    winner_id: int | None = None


class DisputeSupportPaginationSchema(DisputePaginationSchema):
    user_id: int | None = None
