"""Модуль для базовых схем."""

from email_validator import EmailNotValidError, validate_email
from pydantic import BaseModel, Field, field_validator

from src import constants


class PaginationBaseSchema(BaseModel):
    """Базовая схема query параметров для пагинации."""

    offset: int | None = Field(
        default=constants.DEFAULT_QUERY_OFFSET,
        description="Смещение выборки.",
    )
    limit: int | None = Field(
        default=constants.DEFAULT_QUERY_LIMIT,
        description="Размер выборки.",
    )


class DataListGetBaseSchema(BaseModel):
    """Базовая схема для отображения списка сущностей."""

    count: int = Field(
        description="Общее количество сущностей без учета пагинации.",
    )
    data: list = Field(
        description="Список сущностей.",
    )


class EmailBaseSchema(BaseModel):
    """Базовая схема с полем email (str), и его валидацией."""

    email: str = Field(
        description="Email пользователя.",
    )

    @field_validator("email")
    def validate_email(cls, v: str) -> str:
        """Валидация электронной почты пользователя."""
        try:
            validate_email(v)
        except EmailNotValidError as e:
            raise ValueError(str(e))
        return v


class OptionalEmailBaseSchema(BaseModel):
    """Базовая схема с опциональным полем email (str), и его валидацией."""

    email: str | None = Field(
        default=None,
        description="Email пользователя.",
    )

    @field_validator("email")
    def validate_email(cls, v: str | None) -> str | None:
        """Валидация электронной почты пользователя."""
        if v is None:
            return v

        try:
            validate_email(v)
        except EmailNotValidError as e:
            raise ValueError(str(e))
        return v
