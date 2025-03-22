"""Модуль для Pydantic схем пользователей."""

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)

from src.apps.permissions.schemas import PermissionGetSchema
from src.apps.requisites.schemas import RequisiteGetSchema
from src.core.database import Base
from src.lib.base.schemas import DataListGetBaseSchema, PaginationBaseSchema


class UserGetSchema(BaseModel):
    """Pydantic схема для получения пользователя."""

    id: int = Field(description="ID пользователя.")
    email: EmailStr = Field(description="Электронная почта пользователя.")
    balance: int = Field(description="Баланс пользователя.")
    amount_frozen: int = Field(description="Замороженные средства пользователя.")
    is_active: bool = Field(description="Является ли аккаунт пользователя активным.")
    permissions: list[PermissionGetSchema] = Field(
        description="Разрешения пользователя."
    )
    requisites: list[RequisiteGetSchema] = Field(description="Реквизиты пользователя.")
    is_2fa_enabled: bool = Field(description="Является ли 2FA включенным.")

    class Config:
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
        if not isinstance(obj, dict):
            obj = obj.__dict__

        obj["permissions"] = [
            PermissionGetSchema.model_validate(user_permission.permission)
            for user_permission in obj["users_permissions"]
        ]

        return super().model_validate(obj)


class UserLoginSchema(BaseModel):
    """Pydantic схема для авторизации пользователя."""

    email: EmailStr = Field(description="Электронная почта пользователя.")
    password: str = Field(description="Пароль пользователя.")


class UserCreateSchema(BaseModel):
    """Pydantic схема для создания пользователя."""

    email: EmailStr = Field(description="Электронная почта пользователя.")
    permissions_ids: list[int] = Field(description="ID разрешений пользователя.")


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
    permissions_ids: list[int] | None = Field(
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

    id: int | None = Field(
        default=None,
        description="ID пользователя.",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Электронная почта пользователя.",
    )
    permissions_ids: list[int] | None = Field(
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
