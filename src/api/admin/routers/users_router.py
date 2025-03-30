"""Модуль для админского роутера для работы с пользователями."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.schemas import user_schemas
from src.apps.users.service import UserService
from src.core import constants, dependencies

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


# MARK: Post
@router.post(
    "",
    summary="Создать нового пользователя.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.CREATE_USER])
        ),
    ],
)
async def create_user_by_admin_route(
    data: user_schemas.UserCreateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Создать нового пользователя.

    Требуется разрешение: `создать пользователя`.
    """
    return await UserService.create(session, data)


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить данные пользователя по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.GET_USER])
        ),
    ],
)
async def get_user_by_id_route(
    id: int,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить данные пользователя по ID.

    Требуется разрешение: `получить пользователя`.
    """
    return await UserService.get_by_id(session, id)


@router.get(
    "",
    summary="Получить список пользователей.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.GET_USER])
        ),
    ],
)
async def get_users_by_admin_route(
    query_params: user_schemas.UsersPaginationSchema = Query(),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить список пользователей.

    Требуется разрешение: `получить пользователя`.
    """
    return await UserService.get_all(session, query_params)


# MARK: Put
@router.put(
    "/{id}",
    summary="Обновить данные пользователя.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.UPDATE_USER])
        ),
    ],
)
async def update_user_by_admin_route(
    id: int,
    data: user_schemas.UserUpdateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Обновить данные пользователя.

    Требуется разрешение: `обновить пользователя`.
    """
    return await UserService.update(session, id, data)


# MARK: Delete
@router.delete(
    "/{id}",
    summary="Удалить пользователя.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.DELETE_USER])
        ),
    ],
)
async def delete_user_by_admin_route(
    id: int,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Удалить пользователя.

    Требуется разрешение: `удалить пользователя`.
    """
    await UserService.delete(session, id)
