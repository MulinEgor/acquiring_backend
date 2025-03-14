"""Модуль для Pydantic схем разрешений пользователей."""

import uuid

from pydantic import BaseModel


class UsersPermissionsCreateSchema(BaseModel):
    """Схема для создания разрешений пользователей."""

    user_id: uuid.UUID
    permission_id: uuid.UUID
