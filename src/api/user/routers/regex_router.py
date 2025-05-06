from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.regex import schemas
from src.apps.regex.service import RegexService
from src.core import constants, dependencies

router = APIRouter(prefix="/regex", tags=["Регулярные выражения"])


@router.get(
    "",
    summary="Получить все regex с фильтрацией и пагинацией.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.GET_REGEX])
        ),
    ],
)
async def get_all_route(
    query_params: schemas.RegexPaginationSchema = Query(),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить все regex с фильтрацией и пагинацией.

    Требуется разрешение: `получить regex`.
    """
    return await RegexService.get_all(session, query_params)
