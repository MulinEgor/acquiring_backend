"""Модуль для роутера для работы с связями ролей и разрешений."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src import dependencies
from src.dependencies import get_session
from src.roles_permissions import schemas
from src.roles_permissions.service import RolesPermissionsService

roles_permissions_router = APIRouter(
    prefix="/roles-permissions",
    tags=["Связи ролей и разрешений"],
)


# MARK: Create
@roles_permissions_router.post(
    "",
    summary="Администратор. Создать связь роли и разрешения.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def create_route(
    data: schemas.RolesPermissionsCreateSchema,
    session: AsyncSession = Depends(get_session),
):
    return await RolesPermissionsService.create(session, data)


# MARK: Get
@roles_permissions_router.get(
    "/{role_id}/{permission_id}",
    summary="Администратор. Получить связь роли и разрешения по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def get_route(
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    return await RolesPermissionsService.get_by_role_and_permission_ids(
        session,
        role_id,
        permission_id,
    )


@roles_permissions_router.get(
    "",
    summary="Администратор. Получить все связи ролей и разрешений\
             с фильтрацией и пагинацией.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def get_all_route(
    query_params: schemas.RolesPermissionsPaginationSchema = Query(),
    session: AsyncSession = Depends(get_session),
):
    return await RolesPermissionsService.get_all(session, query_params)


# MARK: Delete
@roles_permissions_router.delete(
    "/{role_id}/{permission_id}",
    summary="Администратор. Удалить связь роли и разрешения по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def delete_route(
    role_id: uuid.UUID,
    permission_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    return await RolesPermissionsService.delete_by_role_and_permission_ids(
        session,
        role_id,
        permission_id,
    )
