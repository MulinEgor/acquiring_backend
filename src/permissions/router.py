"""Модуль для роутера для работы с разрешениями."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src import dependencies
from src.permissions import schemas
from src.permissions.enums import PermissionEnum
from src.permissions.service import PermissionService
from src.users.models import UserModel

permissions_router = APIRouter(prefix="/permissions", tags=["Разрешения"])


# MARK: Create
@permissions_router.post(
    "",
    summary="Создать новое разрешение.",
    status_code=status.HTTP_201_CREATED,
)
async def create_route(
    data: schemas.PermissionCreateSchema,
    _: UserModel = Depends(
        dependencies.check_user_permissions([PermissionEnum.CREATE_PERMISSION])
    ),
    session: AsyncSession = Depends(dependencies.get_db_session),
):
    """
    Создать новое разрешение.

    Требуется разрешение: `создать разрешение`.
    """
    return await PermissionService.create(session, data)


# MARK: Get
@permissions_router.get(
    "/{id}",
    summary="Получить разрешение по ID.",
    status_code=status.HTTP_200_OK,
)
async def get_route(
    id: int,
    _: UserModel = Depends(
        dependencies.check_user_permissions([PermissionEnum.GET_PERMISSION])
    ),
    session: AsyncSession = Depends(dependencies.get_db_session),
):
    """
    Получить разрешение по ID.

    Требуется разрешение: `получить разрешение`.
    """
    return await PermissionService.get_by_id(session, id)


@permissions_router.get(
    "",
    summary="Получить все разрешения с фильтрацией и пагинацией.",
    status_code=status.HTTP_200_OK,
)
async def get_all_route(
    query_params: schemas.PermissionPaginationSchema = Query(),
    _: UserModel = Depends(
        dependencies.check_user_permissions([PermissionEnum.GET_PERMISSION])
    ),
    session: AsyncSession = Depends(dependencies.get_db_session),
):
    """
    Получить все разрешения с фильтрацией и пагинацией.

    Требуется разрешение: `получить разрешение`.
    """
    return await PermissionService.get_all(session, query_params)


# MARK: Update
@permissions_router.put(
    "/{id}",
    summary="Обновить разрешение по ID.",
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_route(
    id: int,
    data: schemas.PermissionCreateSchema,
    _: UserModel = Depends(
        dependencies.check_user_permissions([PermissionEnum.UPDATE_PERMISSION])
    ),
    session: AsyncSession = Depends(dependencies.get_db_session),
):
    """
    Обновить разрешение по ID.

    Требуется разрешение: `обновить разрешение`.
    """
    return await PermissionService.update(session, id, data)


# MARK: Delete
@permissions_router.delete(
    "/{id}",
    summary="Удалить разрешение по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_route(
    id: int,
    _: UserModel = Depends(
        dependencies.check_user_permissions([PermissionEnum.DELETE_PERMISSION])
    ),
    session: AsyncSession = Depends(dependencies.get_db_session),
):
    """
    Удалить разрешение по ID.

    Требуется разрешение: `удалить разрешение`.
    """
    return await PermissionService.delete(session, id)
