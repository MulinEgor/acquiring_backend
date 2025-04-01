"""Модуль для роутера админа для работы с реквизитами."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.requisites import schemas
from src.apps.requisites.service import RequisiteService
from src.core import dependencies
from src.core.constants import PermissionEnum
from src.core.dependencies import get_session

router = APIRouter(prefix="/requisites", tags=["Реквизиты"])


# MARK: Post
@router.post(
    "",
    summary="Создать реквизиты.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(dependencies.check_user_permissions([PermissionEnum.CREATE_REQUISITE])),
    ],
)
async def create_requisite_route(
    data: schemas.RequisiteCreateAdminSchema,
    session: AsyncSession = Depends(get_session),
):
    """
    Создать реквизиты.

    Требуется разрешение: `создать реквизиты`.
    """
    return await RequisiteService.create(
        session=session,
        data=data,
    )


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить реквизиты по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(dependencies.check_user_permissions([PermissionEnum.GET_REQUISITE])),
    ],
)
async def get_requisite_route(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Получить реквизиты по ID.

    Требуется разрешение: `получить реквизиты`.
    """
    return await RequisiteService.get_by_id(
        session=session,
        id=id,
    )


@router.get(
    "",
    summary="Получить все реквизиты.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(dependencies.check_user_permissions([PermissionEnum.GET_REQUISITE])),
    ],
)
async def get_requisites_route(
    query_params: schemas.RequisitePaginationAdminSchema = Query(),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить все реквизиты.

    Требуется разрешение: `получить реквизиты`.
    """
    return await RequisiteService.get_all(
        session=session,
        query_params=query_params,
    )


# MARK: Put
@router.put(
    "/{id}",
    summary="Обновить реквизиты по ID.",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(dependencies.check_user_permissions([PermissionEnum.UPDATE_REQUISITE])),
    ],
)
async def update_requisite_route(
    id: int,
    data: schemas.RequisiteUpdateAdminSchema,
    session: AsyncSession = Depends(get_session),
):
    """
    Обновить реквизиты по ID.

    Требуется разрешение: `обновить реквизиты`.
    """
    return await RequisiteService.update(
        session=session,
        id=id,
        data=data,
    )


# MARK: Delete
@router.delete(
    "/{id}",
    summary="Удалить реквизиты по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(dependencies.check_user_permissions([PermissionEnum.DELETE_REQUISITE])),
    ],
)
async def delete_requisite_route(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Удалить реквизиты по ID.

    Требуется разрешение: `удалить реквизиты`.
    """
    return await RequisiteService.delete(
        session=session,
        id=id,
    )
