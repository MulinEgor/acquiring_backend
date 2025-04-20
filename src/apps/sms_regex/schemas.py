from datetime import datetime

from pydantic import BaseModel

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class SmsRegexCreateSchema(BaseModel):
    sender: str
    regex: str


class SmsRegexGetSchema(BaseModel):
    id: int
    sender: str
    regex: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SmsRegexUpdateSchema(BaseModel):
    sender: str | None = None
    regex: str | None = None


class SmsRegexPaginationSchema(PaginationBaseSchema):
    sender: str | None = None
    regex: str | None = None


class SmsRegexListGetSchema(DataListGetBaseSchema):
    data: list[SmsRegexGetSchema]
