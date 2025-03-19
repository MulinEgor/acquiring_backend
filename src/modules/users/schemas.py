"""Модуль для Pydantic схем пользователей."""

import uuid

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    model_serializer,
)

from src.core.base.schemas import DataListGetBaseSchema, PaginationBaseSchema
from src.core.database import Base
from src.modules.permissions.schemas import PermissionGetSchema


class UserGetSchema(BaseModel):
    """Pydantic схема для получения пользователя."""

    id: uuid.UUID = Field(description="ID пользователя.")
    email: EmailStr = Field(description="Электронная почта пользователя.")
    balance: int = Field(description="Баланс пользователя.")
    amount_frozen: int = Field(description="Замороженные средства пользователя.")
    is_active: bool = Field(description="Является ли аккаунт пользователя активным.")
    permissions: list[PermissionGetSchema] = Field(
        description="Разрешения пользователя."
    )
    is_2fa_enabled: bool = Field(description="Является ли 2FA включенным.")

    class Config:
        json_encoders = {uuid.UUID: str}
        from_attributes = True

    @classmethod
    def model_validate(cls, obj: dict | Base) -> "UserGetSchema":
        """
        Пользовательская валидация модели.

        Args:
            obj: Входные данные для валидации

        Returns:
            UserGetSchema: Валидированный объект схемы
        """
        # Здесь можно добавить любую дополнительную логику валидации
        if not isinstance(obj, dict):
            obj = obj.__dict__

        obj["permissions"] = [
            PermissionGetSchema.model_validate(user_permission.permission)
            for user_permission in obj["users_permissions"]
        ]

        # Вызов стандартной валидации
        return super().model_validate(obj)


class UserLoginSchema(BaseModel):
    """Pydantic схема для авторизации пользователя."""

    email: EmailStr = Field(description="Электронная почта пользователя.")
    password: str = Field(description="Пароль пользователя.")


class UserCreateSchema(BaseModel):
    """Pydantic схема для создания пользователя."""

    email: EmailStr = Field(description="Электронная почта пользователя.")
    permissions_ids: list[uuid.UUID] = Field(description="ID разрешений пользователя.")

    @model_serializer
    def serialize_model(self) -> dict[str, str]:
        return {
            "email": self.email,
            "permissions_ids": [
                str(permission_id) for permission_id in self.permissions_ids
            ],
        }


class UserCreatedGetSchema(UserGetSchema):
    """Pydantic схема для получения созданного пользователя."""

    password: str = Field(description="Сгенерированный пароль пользователя.")


class UserCreateRepositorySchema(BaseModel):
    """Pydantic схема для создания пользователя в БД."""

    email: EmailStr = Field(description="Электронная почта пользователя.")
    hashed_password: str = Field(description="Хэшированный пароль пользователя.")


class UserUpdateSchema(BaseModel):
    """Pydantic схема для обновления данных пользователя."""

    email: EmailStr | None = Field(
        default=None,
        description="Электронная почта пользователя.",
    )
    password: str | None = Field(
        default=None,
        description="Пароль пользователя.",
    )
    permissions_ids: list[uuid.UUID] | None = Field(
        default=None,
        description="ID разрешений пользователя.",
    )
    is_active: bool | None = Field(
        default=None,
        description="Является ли аккаунт пользователя активным.",
    )


class UserUpdateRepositorySchema(BaseModel):
    """Pydantic схема для обновления данных пользователя в БД."""

    email: EmailStr | None = Field(
        default=None,
        description="Электронная почта пользователя.",
    )
    hashed_password: str | None = Field(
        default=None,
        description="Хэшированный пароль пользователя.",
    )
    is_active: bool | None = Field(
        default=None,
        description="Является ли аккаунт пользователя активным.",
    )


class UsersListGetSchema(DataListGetBaseSchema):
    """Pydantic схема для получения списка пользователя."""

    data: list[UserGetSchema] = Field(
        description="Список пользователей, соответствующих query параметрам.",
    )


class UsersPaginationSchema(PaginationBaseSchema):
    """
    Основная схема query параметров для запроса
    списка пользователей от имени администратора.
    """

    id: uuid.UUID | None = Field(
        default=None,
        description="ID пользователя.",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Электронная почта пользователя.",
    )
    permissions_ids: list[uuid.UUID] | None = Field(
        default=None,
        description="ID разрешений пользователя.",
    )
    is_active: bool | None = Field(
        default=None,
        description="Является ли аккаунт пользователя активным.",
    )
    is_2fa_enabled: bool | None = Field(
        default=None,
        description="Является ли 2FA включенным.",
    )
