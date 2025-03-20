"""Модуль для админского роутера для работы с пользователями."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users import schemas
from src.apps.users.models import UserModel
from src.apps.users.service import UserService
from src.core import constants, dependencies

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


# MARK: Get
@router.get(
    "/me",
    summary="Получить данные текущего пользователя.",
    status_code=status.HTTP_200_OK,
)
async def get_current_user_route(
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.GET_MY_USER])
    ),
):
    """
    Получить данные текущего пользователя.

    Требуется разрешение: `получить своего пользователя`.
    """
    return schemas.UserGetSchema.model_validate(user)


@router.get(
    "/{id}",
    summary="Получить данные пользователя по ID.",
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id_route(
    id: int,
    _=Depends(dependencies.check_user_permissions([constants.PermissionEnum.GET_USER])),
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
)
async def get_users_by_admin_route(
    query_params: schemas.UsersPaginationSchema = Query(),
    _=Depends(dependencies.check_user_permissions([constants.PermissionEnum.GET_USER])),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить список пользователей.

    Требуется разрешение: `получить пользователя`.
    """
    return await UserService.get_all(session, query_params)


# MARK: Post
@router.post(
    "",
    summary="Создать нового пользователя.",
    status_code=status.HTTP_201_CREATED,
)
async def create_user_by_admin_route(
    data: schemas.UserCreateSchema,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.CREATE_USER])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Создать нового пользователя.

    Требуется разрешение: `создать пользователя`.
    """
    return await UserService.create(session, data)


# MARK: Put
@router.put(
    "/{id}",
    summary="Обновить данные пользователя.",
    status_code=status.HTTP_200_OK,
)
async def update_user_by_admin_route(
    id: int,
    data: schemas.UserUpdateSchema,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.UPDATE_USER])
    ),
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
)
async def delete_user_by_admin_route(
    id: int,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.DELETE_USER])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Удалить пользователя.

    Требуется разрешение: `удалить пользователя`.
    """
    await UserService.delete(session, id)
