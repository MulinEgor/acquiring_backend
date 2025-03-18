"""Модуль для Pydantic схем пользователей."""

from pydantic import (
    Field,
)

from src.base.schemas import (
    DataListGetBaseSchema,
    EmailBaseSchema,
    OptionalEmailBaseSchema,
)
from src.database import Base
from src.permissions.schemas import PermissionGetSchema


class UserGetSchema(EmailBaseSchema):
    """Pydantic схема для получения пользователя."""

    id: int = Field(description="ID пользователя.")
    balance: int = Field(description="Баланс пользователя.")
    amount_frozen: int = Field(description="Замороженные средства пользователя.")
    is_active: bool = Field(description="Является ли аккаунт пользователя активным.")
    permissions: list[PermissionGetSchema] = Field(
        description="Разрешения пользователя."
    )
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
        # Здесь можно добавить любую дополнительную логику валидации
        if not isinstance(obj, dict):
            obj = obj.__dict__

        obj["permissions"] = [
            PermissionGetSchema.model_validate(user_permission.permission)
            for user_permission in obj["users_permissions"]
        ]

        return super().model_validate(obj)


class UserLoginSchema(EmailBaseSchema):
    """Pydantic схема для авторизации пользователя."""

    password: str = Field(description="Пароль пользователя.")


class UserCreateSchema(EmailBaseSchema):
    """Pydantic схема для создания пользователя."""

    permissions_ids: list[int] = Field(description="ID разрешений пользователя.")


class UserCreatedGetSchema(UserGetSchema):
    """Pydantic схема для получения созданного пользователя."""

    password: str = Field(description="Сгенерированный пароль пользователя.")


class UserCreateRepositorySchema(EmailBaseSchema):
    """Pydantic схема для создания пользователя в БД."""

    hashed_password: str = Field(description="Хэшированный пароль пользователя.")


class UserUpdateSchema(OptionalEmailBaseSchema):
    """Pydantic схема для обновления данных пользователя."""

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


class UserUpdateRepositorySchema(OptionalEmailBaseSchema):
    """Pydantic схема для обновления данных пользователя в БД."""

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


class UsersPaginationSchema(OptionalEmailBaseSchema):
    """
    Основная схема query параметров для запроса
    списка пользователей от имени администратора.
    """

    id: int | None = Field(
        default=None,
        description="ID пользователя.",
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
    asc: bool = Field(
        default=False,
        description=(
            "Порядок сортировки пользователей по дате создания. "
            "По умолчанию — от новых к старым."
        ),
    )
