"""Модуль для Pydantic схем пользователей."""

import uuid

from fastapi import HTTPException, status
from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from src.base.schemas import DataListGetBaseSchema, PaginationBaseSchema
from src.roles.models import RoleEnum
from src.roles.schemas import RoleGetSchema


class UserGetSchema(BaseModel):
    """Pydantic схема для получения пользователя."""

    id: uuid.UUID = Field(description="ID пользователя.")
    email: str = Field(description="Электронная почта пользователя.")
    role: RoleGetSchema = Field(description="Роль пользователя.")

    class Config:
        json_encoders = {uuid.UUID: str}
        from_attributes = True


class UserLoginSchema(BaseModel):
    """Pydantic схема для авторизации пользователя."""

    email: str = Field(description="Электронная почта пользователя.")
    password: str = Field(description="Пароль пользователя.")


class UserCreateSchema(BaseModel):
    """Pydantic схема для создания пользователя."""

    email: str = Field(description="Электронная почта пользователя.")
    role_name: RoleEnum = Field(description="Название роли пользователя.")


class UserCreatedGetSchema(UserGetSchema):
    """Pydantic схема для получения созданного пользователя."""

    password: str = Field(description="Сгенерированный пароль пользователя.")


class UserCreateRepositorySchema(BaseModel):
    """Pydantic схема для создания пользователя в БД."""

    email: str = Field(description="Электронная почта пользователя.")
    hashed_password: str = Field(description="Хэшированный пароль пользователя.")
    role_id: uuid.UUID = Field(description="ID роли пользователя.")


class UserUpdateSchema(BaseModel):
    """Pydantic схема для обновления данных пользователя."""

    email: str | None = Field(
        default=None,
        description="Электронная почта пользователя.",
    )
    password: str | None = Field(
        default=None,
        description="Пароль пользователя.",
    )
    role_name: RoleEnum | None = Field(
        default=None,
        description="Название роли пользователя.",
    )


class UserUpdateRepositorySchema(BaseModel):
    """Pydantic схема для обновления данных пользователя в БД."""

    email: str | None = Field(
        default=None,
        description="Электронная почта пользователя.",
    )
    hashed_password: str | None = Field(
        default=None,
        description="Хэшированный пароль пользователя.",
    )
    role_id: uuid.UUID | None = Field(
        default=None,
        description="ID роли пользователя.",
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
    email: str | None = Field(
        default=None,
        description="Электронная почта пользователя.",
    )
    role_name: str | None = Field(
        default=None,
        description="Название роли пользователя.",
    )
    asc: bool = Field(
        default=False,
        description=(
            "Порядок сортировки пользователей по дате создания. "
            "По умолчанию — от новых к старым."
        ),
    )

    @field_validator("role_name")
    def role_validator(cls, v: str) -> str:
        """Валидация названия роли пользователя."""

        if v not in [role.value for role in RoleEnum]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Неверное название роли пользователя",
            )

        return v
