from pydantic import BaseModel


class UsersPermissionsCreateSchema(BaseModel):
    """Схема для создания разрешений пользователей."""

    user_id: int
    permission_id: int
