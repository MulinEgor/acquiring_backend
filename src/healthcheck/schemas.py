"""Модуль для Pydantic схем для модуля healthcheck."""

from typing import Literal

from pydantic import BaseModel, Field

from src.settings import settings


class HealthCheckSchema(BaseModel):
    """Схема ответа для проверки состояния работы API."""

    mode: Literal["DEV", "TEST", "PROD"] = Field(
        default=settings.MODE,
        description="Режим, в котором работает API.",
    )
    version: str = Field(
        default=settings.APP_VERSION,
        description="Версия API. Соответствует хэшу актуального коммита.",
    )
    status: str = Field(
        default="OK",
        description="Статус API.",
    )
