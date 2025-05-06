from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.regex import schemas
from src.apps.regex.service import RegexService
from src.core import constants, dependencies

router = APIRouter(prefix="/regex", tags=["Регулярные выражения"])


# MARK: Post
@router.post(
    "",
    summary="Создать новое regex.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.CREATE_REGEX])
        ),
    ],
)
async def create_route(
    data: schemas.RegexCreateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Создать новое regex.

    Требуется разрешение: `создать regex`.
    """
    return await RegexService.create(session, data)


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить regex по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.GET_REGEX])
        ),
    ],
)
async def get_route(
    id: int,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить regex по ID.

    Требуется разрешение: `получить regex`.
    """
    return await RegexService.get_by_id(session, id)


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


# MARK: Update
@router.put(
    "/{id}",
    summary="Обновить regex по ID.",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.UPDATE_REGEX])
        ),
    ],
)
async def update_route(
    id: int,
    data: schemas.RegexUpdateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Обновить regex по ID.

    Требуется разрешение: `обновить regex`.
    """
    return await RegexService.update(session, id, data)


# MARK: Delete
@router.delete(
    "/{id}",
    summary="Удалить regex по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.DELETE_REGEX])
        ),
    ],
)
async def delete_route(
    id: int,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Удалить regex по ID.

    Требуется разрешение: `удалить regex`.
    """
    return await RegexService.delete(session, id)
