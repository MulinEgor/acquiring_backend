"""Модуль для маршрутов пользователей."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

import src.users.schemas as schemas
from src import dependencies
from src.users.models import UserModel
from src.users.service import UserService

users_router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


# MARK: Get
@users_router.get(
    "/me",
    summary="Авторизованный пользователь. Получить данные текущего пользователя.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.get_current_user)],
)
async def get_current_user_route(
    user: UserModel = Depends(dependencies.get_current_user),
):
    return schemas.UserGetSchema.model_validate(user)


@users_router.get(
    "/{id}",
    summary="Администратор. Получить данные пользователя по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def get_user_by_id_route(
    id: str,
    session: AsyncSession = Depends(dependencies.get_session),
):
    return await UserService.get_by_id(session, id)


@users_router.get(
    "",
    summary="Администратор. Получить список пользователей.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def get_users_by_admin_route(
    query_params: schemas.UsersPaginationSchema = Query(),
    session: AsyncSession = Depends(dependencies.get_session),
):
    return await UserService.get_all(session, query_params)


# MARK: Post
@users_router.post(
    "",
    summary="Администратор. Создать нового пользователя.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def create_user_by_admin_route(
    data: schemas.UserCreateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    return await UserService.create(session, data)


# MARK: Put
@users_router.put(
    "/{id}",
    summary="Администратор. Обновить данные пользователя.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def update_user_by_admin_route(
    id: str,
    data: schemas.UserUpdateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    return await UserService.update(session, id, data)


# MARK: Delete
@users_router.delete(
    "/{id}",
    summary="Администратор. Удалить пользователя.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependencies.get_current_admin)],
)
async def delete_user_by_admin_route(
    id: str,
    session: AsyncSession = Depends(dependencies.get_session),
):
    await UserService.delete(session, id)
