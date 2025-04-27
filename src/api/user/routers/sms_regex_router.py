from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.sms_regex import schemas
from src.apps.sms_regex.service import SmsRegexService
from src.core import constants, dependencies

router = APIRouter(prefix="/sms-regex", tags=["SMS-regex"])


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
