"""Модуль для админского роутера диспутов."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.disputes import schemas
from src.apps.disputes.service import DisputeService
from src.core import constants, dependencies

router = APIRouter(prefix="/disputes", tags=["Диспуты"])


# MARK: Post
@router.post(
    "",
    summary="Создать диспут",
    status_code=status.HTTP_201_CREATED,
)
async def create_dispute_route(
    data: schemas.DisputeCreateSchema,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.CREATE_DISPUTE])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    return await DisputeService.create(session=session, data=data)


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить данные диспута по ID.",
    status_code=status.HTTP_200_OK,
)
async def get_dispute_by_id_route(
    id: int,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.GET_DISPUTE])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить данные кошелька по адресу.

    Требуется разрешение: `получить диспут`.
    """
    return await DisputeService.get_by_id(session=session, id=id)


@router.get(
    "",
    summary="Получить список диспутов.",
    status_code=status.HTTP_200_OK,
)
async def get_disputes_by_admin_route(
    query_params: schemas.DisputePaginationSchema = Query(),
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.GET_DISPUTE])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить список диспутов.

    Требуется разрешение: `получить диспут`.
    """
    return await DisputeService.get_all(session=session, query_params=query_params)


# MARK: Put
@router.put(
    "/{id}",
    summary="Обновить диспут по ID.",
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_dispute_by_id_route(
    id: int,
    data: schemas.DisputeUpdateSchema,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.UPDATE_DISPUTE])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Обновить диспут по ID.

    Требуется разрешение: `обновить диспут`.
    """
    return await DisputeService.update(session=session, id=id, data=data)


# MARK: Delete
@router.delete(
    "/{id}",
    summary="Удалить диспут по ID.",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_dispute_by_id_route(
    id: int,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.DELETE_DISPUTE])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Удалить диспут по ID.

    Требуется разрешение: `удалить диспут`.
    """
    return await DisputeService.delete(session=session, id=id)
