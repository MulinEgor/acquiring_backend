from typing import Literal

from pydantic import BaseModel

from src.core.settings import settings


class HealthCheckSchema(BaseModel):
    """Схема ответа для проверки состояния работы API."""

    mode: Literal["DEV", "TEST", "PROD"] = settings.MODE
    version: str = settings.APP_VERSION
    status: str = "OK"
