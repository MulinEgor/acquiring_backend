"""Модуль для Pydantic схем для работы с связями ролей и разрешений."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.base.schemas import DataListGetBaseSchema, PaginationBaseSchema
from src.permissions.schemas import PermissionGetSchema
from src.roles.schemas import RoleGetSchema


class RolesPermissionsCreateSchema(BaseModel):
    """Схема для создания связи ролей и разрешений."""

    role_id: uuid.UUID = Field(description="ID роли.")
    permission_id: uuid.UUID = Field(description="ID разрешения.")


class RolesPermissionsGetSchema(BaseModel):
    """Схема для получения связи ролей и разрешений."""

    role: RoleGetSchema = Field(description="Роль.")
    permission: PermissionGetSchema = Field(description="Разрешение.")
    created_at: datetime = Field(description="Дата создания.")
    updated_at: datetime = Field(description="Дата обновления.")

    class Config:
        from_attributes = True


class RolesPermissionsPaginationSchema(PaginationBaseSchema):
    """Схема для пагинации связей ролей и разрешений."""

    role_id: uuid.UUID | None = Field(
        default=None,
        description="ID роли.",
    )
    permission_id: uuid.UUID | None = Field(
        default=None,
        description="ID разрешения.",
    )
    asc: bool = Field(
        default=True,
        description="Сортировка по дате создания.",
    )


class RolesPermissionsListGetSchema(DataListGetBaseSchema):
    """Схема для получения списка связей ролей и разрешений."""

    data: list[RolesPermissionsGetSchema] = Field(
        description="Список связей ролей и разрешений."
    )
