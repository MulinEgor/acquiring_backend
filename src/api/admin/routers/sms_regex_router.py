from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.sms_regex import schemas
from src.apps.sms_regex.service import SmsRegexService
from src.core import constants, dependencies

router = APIRouter(prefix="/sms-regex", tags=["Регулярные выражения для SMS"])


# MARK: Post
@router.post(
    "",
    summary="Создать новое sms-regex.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.CREATE_SMS_REGEX]
            )
        ),
    ],
)
async def create_route(
    data: schemas.SmsRegexCreateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Создать новое sms-regex.

    Требуется разрешение: `создать sms-regex`.
    """
    return await SmsRegexService.create(session, data)


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить sms-regex по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.GET_SMS_REGEX]
            )
        ),
    ],
)
async def get_route(
    id: int,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить sms-regex по ID.

    Требуется разрешение: `получить sms-regex`.
    """
    return await SmsRegexService.get_by_id(session, id)


@router.get(
    "",
    summary="Получить все sms-regex с фильтрацией и пагинацией.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.GET_SMS_REGEX]
            )
        ),
    ],
)
async def get_all_route(
    query_params: schemas.SmsRegexPaginationSchema = Query(),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить все sms-regex с фильтрацией и пагинацией.

    Требуется разрешение: `получить sms-regex`.
    """
    return await SmsRegexService.get_all(session, query_params)


# MARK: Update
@router.put(
    "/{id}",
    summary="Обновить sms-regex по ID.",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.UPDATE_SMS_REGEX]
            )
        ),
    ],
)
async def update_route(
    id: int,
    data: schemas.SmsRegexUpdateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Обновить sms-regex по ID.

    Требуется разрешение: `обновить sms-regex`.
    """
    return await SmsRegexService.update(session, id, data)


# MARK: Delete
@router.delete(
    "/{id}",
    summary="Удалить sms-regex по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.DELETE_SMS_REGEX]
            )
        ),
    ],
)
async def delete_route(
    id: int,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Удалить sms-regex по ID.

    Требуется разрешение: `удалить sms-regex`.
    """
    return await SmsRegexService.delete(session, id)
