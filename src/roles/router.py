"""Модуль для роутера для работы с ролямм."""

import uuid

from fastapi import APIRouter, Depends, status

from src import dependencies
from src.roles import schemas
from src.roles.service import RoleService

roles_router = APIRouter(prefix="/roles", tags=["Роли"])


# MARK: Create
@roles_router.post(
    "",
    summary="Администратор. Создать новую роль.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def create_route(
    data: schemas.RoleCreateSchema,
):
    return await RoleService.create(data)


# MARK: Get
@roles_router.get(
    "/{id}",
    summary="Администратор. Получить роль по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def get_route(
    id: uuid.UUID,
):
    return await RoleService.get_by_id(id)


@roles_router.get(
    "",
    summary="Администратор. Получить все роли с фильтрацией и пагинацией.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def get_all_route(
    query_params: schemas.RolePaginationSchema,
):
    return await RoleService.get_all(query_params)


# MARK: Update
@roles_router.put(
    "/{id}",
    summary="Администратор. Обновить роль по ID.",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def update_route(
    id: uuid.UUID,
    data: schemas.RoleCreateSchema,
):
    """Обновить роль по ID."""

    return await RoleService.update(id, data)


# MARK: Delete
@roles_router.delete(
    "/{id}",
    summary="Администратор. Удалить роль по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def delete_route(
    id: uuid.UUID,
):
    """Удалить роль по ID."""

    return await RoleService.delete(id)
