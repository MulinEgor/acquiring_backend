from datetime import datetime

from pydantic import BaseModel

from src.apps.regex.model import RegexType
from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class RegexCreateSchema(BaseModel):
    sender: str
    regex: str
    is_card: bool
    type: RegexType


class RegexGetSchema(BaseModel):
    id: int
    sender: str
    regex: str
    is_card: bool
    type: RegexType
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegexUpdateSchema(BaseModel):
    sender: str | None = None
    regex: str | None = None
    is_card: bool | None = None
    type: RegexType | None = None


class RegexPaginationSchema(PaginationBaseSchema):
    sender: str | None = None
    regex: str | None = None
    is_card: bool | None = None
    type: RegexType | None = None


class RegexListGetSchema(DataListGetBaseSchema):
    data: list[RegexGetSchema]
