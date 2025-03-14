"""Модуль для роутера для работы с разрешениями."""

import uuid

from fastapi import APIRouter, Depends, status

from src import dependencies
from src.permissions import schemas
from src.permissions.service import PermissionService

permissions_router = APIRouter(prefix="/permissions", tags=["Разрешения"])


# MARK: Create
@permissions_router.post(
    "",
    summary="Администратор. Создать новое разрешение.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def create_route(
    data: schemas.PermissionCreateSchema,
):
    return await PermissionService.create(data)


# MARK: Get
@permissions_router.get(
    "/{id}",
    summary="Администратор. Получить разрешение по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def get_route(
    id: uuid.UUID,
):
    return await PermissionService.get_by_id(id)


@permissions_router.get(
    "",
    summary="Администратор. Получить все разрешения с фильтрацией и пагинацией.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def get_all_route(
    query_params: schemas.PermissionPaginationSchema,
):
    return await PermissionService.get_all(query_params)


# MARK: Update
@permissions_router.put(
    "/{id}",
    summary="Администратор. Обновить разрешение по ID.",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def update_route(
    id: uuid.UUID,
    data: schemas.PermissionCreateSchema,
):
    return await PermissionService.update(id, data)


# MARK: Delete
@permissions_router.delete(
    "/{id}",
    summary="Администратор. Удалить разрешение по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def delete_route(
    id: uuid.UUID,
):
    return await PermissionService.delete(id)
