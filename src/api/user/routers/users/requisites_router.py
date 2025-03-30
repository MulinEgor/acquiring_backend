"""Модуль для роутера трейдера для работы с реквизитами."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.requisites import schemas
from src.apps.requisites.service import RequisiteService
from src.apps.users.model import UserModel
from src.core import dependencies
from src.core.constants import PermissionEnum
from src.core.dependencies import get_session

router = APIRouter(prefix="/requisites", tags=["Реквизиты"])


# MARK: Post
@router.post(
    "",
    summary="Создать свои реквизиты.",
    status_code=status.HTTP_201_CREATED,
)
async def create_requisite_route(
    data: schemas.RequisiteCreateSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    _: bool = Depends(
        dependencies.check_user_permissions([PermissionEnum.CREATE_MY_REQUISITE])
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Создать свои реквизиты.

    Требуется разрешение: `создать свои реквизиты`.
    """
    return await RequisiteService.create(
        session=session,
        data=schemas.RequisiteCreateAdminSchema(user_id=user.id, **data.model_dump()),
    )


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить свои реквизиты по ID.",
    status_code=status.HTTP_200_OK,
)
async def get_my_requisite_route(
    id: int,
    user: UserModel = Depends(dependencies.get_current_user),
    _: bool = Depends(
        dependencies.check_user_permissions([PermissionEnum.GET_MY_REQUISITE])
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить свои реквизиты по ID.

    Требуется разрешение: `получить свои реквизиты`.
    """
    return await RequisiteService.get_by_id(
        session=session,
        id=id,
        user=user,
    )


@router.get(
    "",
    summary="Получить все свои реквизиты.",
    status_code=status.HTTP_200_OK,
)
async def get_my_requisites_route(
    query_params: schemas.RequisitePaginationSchema = Query(),
    user: UserModel = Depends(dependencies.get_current_user),
    _: bool = Depends(
        dependencies.check_user_permissions([PermissionEnum.GET_MY_REQUISITE])
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить все свои реквизиты.

    Требуется разрешение: `получить свои реквизиты`.
    """
    return await RequisiteService.get_all(
        session=session,
        query_params=query_params,
        user_id=user.id,
    )


# MARK: Put
@router.put(
    "/{id}",
    summary="Обновить свои реквизиты по ID.",
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_my_requisite_route(
    id: int,
    data: schemas.RequisiteUpdateSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    _: bool = Depends(
        dependencies.check_user_permissions([PermissionEnum.UPDATE_MY_REQUISITE])
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Обновить свои реквизиты по ID.

    Требуется разрешение: `обновить свои реквизиты`.
    """
    return await RequisiteService.update(
        session=session,
        id=id,
        data=data,
        user=user,
    )


# MARK: Delete
@router.delete(
    "/{id}",
    summary="Удалить свои реквизиты по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_my_requisite_route(
    id: int,
    user: UserModel = Depends(dependencies.get_current_user),
    _: bool = Depends(
        dependencies.check_user_permissions([PermissionEnum.DELETE_MY_REQUISITE])
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Удалить свои реквизиты по ID.

    Требуется разрешение: `удалить свои реквизиты`.
    """
    return await RequisiteService.delete(
        session=session,
        id=id,
        user=user,
    )
