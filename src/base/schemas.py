"""Модуль для базовых схем."""

from pydantic import BaseModel, Field

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
    asc: bool | None = Field(
        default=True,
        description="Сортировка по возрастанию.",
    )


class DataListGetBaseSchema(BaseModel):
    """Базовая схема для отображения списка сущностей."""

    count: int = Field(
        description="Общее количество сущностей без учета пагинации.",
    )
    data: list = Field(
        description="Список сущностей.",
    )
