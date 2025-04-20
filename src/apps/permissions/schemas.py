from datetime import datetime

from pydantic import BaseModel

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class PermissionCreateSchema(BaseModel):
    name: str


class PermissionGetSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionPaginationSchema(PaginationBaseSchema):
    name: str | None = None


class PermissionListGetSchema(DataListGetBaseSchema):
    data: list[PermissionGetSchema]
