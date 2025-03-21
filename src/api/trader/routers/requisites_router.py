"""Модуль для роутера трейдера для работы с реквизитами."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.requisites import schemas
from src.apps.requisites.service import RequisiteService
from src.apps.users.models import UserModel
from src.core import dependencies
from src.core.constants import PermissionEnum
from src.core.dependencies import get_session

router = APIRouter(prefix="/requisites", tags=["Реквизиты"])


# MARK: POST
@router.post("/me", status_code=status.HTTP_201_CREATED)
async def create_requisite(
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


# MARK: GET
@router.get("/me/{id}", status_code=status.HTTP_200_OK)
async def get_my_requisite(
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


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_my_requisites(
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


# MARK: PUT
@router.put("/me/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_my_requisite(
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


# MARK: DELETE
@router.delete("/me/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_requisite(
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
