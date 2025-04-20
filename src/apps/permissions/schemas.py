from datetime import datetime

from pydantic import BaseModel

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class PermissionCreateSchema(BaseModel):
    """Схема для создания разрешения."""

    name: str


class PermissionGetSchema(BaseModel):
    """Схема для получения разрешения."""

    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionPaginationSchema(PaginationBaseSchema):
    """Схема для пагинации разрешений."""

    name: str | None = None


class PermissionListGetSchema(DataListGetBaseSchema):
    """Схема для получения списка разрешений."""

    data: list[PermissionGetSchema]
