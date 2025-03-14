"""Модулья для сервисов для работы с разрешениями."""

from src.base.service import BaseService
from src.permissions import schemas
from src.permissions.models import PermissionModel
from src.permissions.repository import PermissionRepository


class PermissionService(
    BaseService[
        PermissionModel,
        schemas.PermissionCreateSchema,
        schemas.PermissionGetSchema,
        schemas.PermissionPaginationSchema,
        schemas.PermissionListGetSchema,
        schemas.PermissionCreateSchema,
    ],
):
    """Сервис для работы с разрешениями."""

    repository = PermissionRepository
