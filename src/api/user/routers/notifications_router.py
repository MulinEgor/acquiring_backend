"""Модуль для роутера уведомлений."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.notifications import schemas
from src.apps.notifications.repository import NotificationRepository
from src.apps.notifications.service import NotificationService
from src.apps.users.model import UserModel
from src.core import constants, dependencies

router = APIRouter(
    prefix="/notifications",
    tags=["Уведомления"],
)


# MARK: Get
@router.get(
    "",
    summary="Получить свои уведомления.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.GET_MY_NOTIFICATION]
            )
        ),
    ],
)
async def get_my_notifications_route(
    query_params: schemas.NotificationPaginationSchema = Query(),
    user: UserModel = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
) -> schemas.NotificationListSchema:
    """
    Получить уведомления с пагинацией для текущего пользователя.

    Требуется разрешение: `получить свои уведомления`.
    """
    return await NotificationService.get_all(
        session=session,
        query_params=query_params,
        user_id=user.id,
    )


# MARK: Patch
@router.patch(
    "",
    summary="Прочитать свои уведомления.",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.READ_MY_NOTIFICATION]
            )
        ),
    ],
)
async def read_my_notifications_route(
    data: schemas.NotificationReadSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
) -> None:
    """
    Прочитать уведомления.

    Требуется разрешение: `прочитать свои уведомления`.
    """
    return await NotificationRepository.read_all(
        session=session,
        notification_ids=data.notification_ids,
        user_id=user.id,
    )
