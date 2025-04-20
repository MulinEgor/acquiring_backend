from fastapi import APIRouter, status

from src.apps.healthcheck.schemas import HealthCheckSchema

router = APIRouter(prefix="/health_check", tags=["Проверка состояния работы API"])


@router.get(
    path="",
    summary="Проверить состояние работы API",
    status_code=status.HTTP_200_OK,
)
async def health_check_route() -> HealthCheckSchema:
    """Проверить состояние работы API."""

    return HealthCheckSchema()
