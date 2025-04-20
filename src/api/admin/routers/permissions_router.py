from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.permissions import schemas
from src.apps.permissions.service import PermissionService
from src.core import constants, dependencies

router = APIRouter(prefix="/permissions", tags=["Разрешения"])


# MARK: Post
@router.post(
    "",
    summary="Создать новое разрешение.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.CREATE_PERMISSION]
            )
        ),
    ],
)
async def create_route(
    data: schemas.PermissionCreateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Создать новое разрешение.

    Требуется разрешение: `создать разрешение`.
    """
    return await PermissionService.create(session, data)


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить разрешение по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.GET_PERMISSION]
            )
        ),
    ],
)
async def get_route(
    id: int,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить разрешение по ID.

    Требуется разрешение: `получить разрешение`.
    """
    return await PermissionService.get_by_id(session, id)


@router.get(
    "",
    summary="Получить все разрешения с фильтрацией и пагинацией.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.GET_PERMISSION]
            )
        ),
    ],
)
async def get_all_route(
    query_params: schemas.PermissionPaginationSchema = Query(),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить все разрешения с фильтрацией и пагинацией.

    Требуется разрешение: `получить разрешение`.
    """
    return await PermissionService.get_all(session, query_params)


# MARK: Update
@router.put(
    "/{id}",
    summary="Обновить разрешение по ID.",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.UPDATE_PERMISSION]
            )
        ),
    ],
)
async def update_route(
    id: int,
    data: schemas.PermissionCreateSchema,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Обновить разрешение по ID.

    Требуется разрешение: `обновить разрешение`.
    """
    return await PermissionService.update(session, id, data)


# MARK: Delete
@router.delete(
    "/{id}",
    summary="Удалить разрешение по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.DELETE_PERMISSION]
            )
        ),
    ],
)
async def delete_route(
    id: int,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Удалить разрешение по ID.

    Требуется разрешение: `удалить разрешение`.
    """
    return await PermissionService.delete(session, id)
