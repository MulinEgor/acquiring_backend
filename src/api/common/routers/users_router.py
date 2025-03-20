"""Модуль для общего роутера для работы с пользователями."""

from fastapi import APIRouter, Depends, status

from src.apps.users import schemas
from src.apps.users.models import UserModel
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
