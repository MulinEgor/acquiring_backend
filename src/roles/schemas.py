"""Модулья для Pydantic схем для работы с ролями."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class RoleCreateSchema(BaseModel):
    """Схема для создания роли."""

    name: str = Field(description="Название роли.")


class RoleGetSchema(BaseModel):
    """Схема для получения роли."""

    id: uuid.UUID = Field(description="ID роли.")
    name: str = Field(description="Название роли.")
    created_at: datetime = Field(description="Дата создания роли.")
    updated_at: datetime = Field(description="Дата обновления роли.")

    class Config:
        from_attributes = True


class RolePaginationSchema(PaginationBaseSchema):
    """Схема для пагинации ролей."""

    name: str | None = Field(
        default=None,
        description="Название роли.",
    )
    asc: bool = Field(
        default=True,
        description="Сортировка по дате создания.",
    )


class RoleListGetSchema(DataListGetBaseSchema):
    """Схема для получения списка ролей."""

    data: list[RoleGetSchema] = Field(description="Список ролей.")
