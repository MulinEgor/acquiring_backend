"""Модуль для тестирования роутера src.healthcheck.health_check_router"""

import httpx
from fastapi import status

from src.core.settings import settings
from src.modules.healthcheck import HealthCheckSchema, health_check_router
from tests.integration.conftest import BaseTestRouter


class TestHealtcheckRouter(BaseTestRouter):
    """Класс для тестирования роутера health_check_router."""

    router = health_check_router

    async def test_healthcheck(
        self,
        router_client: httpx.AsyncClient,
    ):
        """Возможно проверить состояние работы API."""

        response = await router_client.get(url="/health_check")

        health_check_data = HealthCheckSchema(**response.json())

        assert response.status_code == status.HTTP_200_OK
        assert health_check_data.mode == settings.MODE
        assert health_check_data.version == settings.APP_VERSION
        assert health_check_data.status == "OK"
