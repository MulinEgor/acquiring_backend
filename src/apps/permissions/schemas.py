"""Модулья для Pydantic схем для работы с разрешениями."""

from datetime import datetime

from pydantic import BaseModel, Field

from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class PermissionCreateSchema(BaseModel):
    """Схема для создания разрешения."""

    name: str = Field(description="Название разрешения.")


class PermissionGetSchema(BaseModel):
    """Схема для получения разрешения."""

    id: int = Field(description="ID разрешения.")
    name: str = Field(description="Название разрешения.")
    created_at: datetime = Field(description="Дата создания разрешения.")
    updated_at: datetime = Field(description="Дата обновления разрешения.")

    class Config:
        from_attributes = True


class PermissionPaginationSchema(PaginationBaseSchema):
    """Схема для пагинации разрешений."""

    name: str | None = Field(
        default=None,
        description="Название разрешения.",
    )


class PermissionListGetSchema(DataListGetBaseSchema):
    """Схема для получения списка разрешений."""

    data: list[PermissionGetSchema] = Field(description="Список разрешений.")
