"""Модуль для маршрутов проверки состояния работы API."""

from fastapi import APIRouter, status

from src.healthcheck.schemas import HealthCheckSchema

health_check_router = APIRouter(prefix="/health_check", tags=["Health Check"])


@health_check_router.get(
    path="",
    summary="Проверить состояние работы API",
    status_code=status.HTTP_200_OK,
)
async def health_check() -> HealthCheckSchema:
    """Проверить состояние работы API."""

    return HealthCheckSchema()
