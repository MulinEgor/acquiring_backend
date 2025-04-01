"""Модуль для роутера админа для работы с уведомлениями."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.notifications import schemas
from src.apps.notifications.service import NotificationService
from src.core import dependencies
from src.core.constants import PermissionEnum
from src.core.dependencies import get_session

router = APIRouter(prefix="/notifications", tags=["Уведомления"])


# MARK: Post
@router.post(
    "",
    summary="Создать уведомление.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([PermissionEnum.CREATE_NOTIFICATION])
        ),
    ],
)
async def create_notification_route(
    data: schemas.NotificationCreateSchema,
    session: AsyncSession = Depends(get_session),
):
    """
    Создать уведомление.

    Требуется разрешение: `создать уведомление`.
    """
    return await NotificationService.create(
        session=session,
        data=data,
    )


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить уведомление по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(dependencies.check_user_permissions([PermissionEnum.GET_NOTIFICATION])),
    ],
)
async def get_notification_route(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Получить уведомление по ID.

    Требуется разрешение: `получить уведомление`.
    """
    return await NotificationService.get_by_id(
        session=session,
        id=id,
    )


@router.get(
    "",
    summary="Получить все уведомления.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(dependencies.check_user_permissions([PermissionEnum.GET_NOTIFICATION])),
    ],
)
async def get_notifications_route(
    query_params: schemas.NotificationPaginationSchema = Query(),
    session: AsyncSession = Depends(get_session),
):
    """
    Получить все уведомления.

    Требуется разрешение: `получить уведомление`.
    """
    return await NotificationService.get_all(
        session=session,
        query_params=query_params,
    )


# MARK: Put
@router.put(
    "/{id}",
    summary="Обновить уведомление по ID.",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([PermissionEnum.UPDATE_NOTIFICATION])
        ),
    ],
)
async def update_notification_route(
    id: int,
    data: schemas.NotificationUpdateSchema,
    session: AsyncSession = Depends(get_session),
):
    """
    Обновить уведомление по ID.

    Требуется разрешение: `обновить уведомление`.
    """
    return await NotificationService.update(
        session=session,
        id=id,
        data=data,
    )


# MARK: Delete
@router.delete(
    "/{id}",
    summary="Удалить уведомление по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([PermissionEnum.DELETE_NOTIFICATION])
        ),
    ],
)
async def delete_notification_route(
    id: int,
    session: AsyncSession = Depends(get_session),
):
    """
    Удалить уведомление по ID.

    Требуется разрешение: `удалить уведомление`.
    """
    return await NotificationService.delete(
        session=session,
        id=id,
    )
