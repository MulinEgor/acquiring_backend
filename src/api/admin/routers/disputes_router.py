"""Модуль для админского роутера диспутов."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.disputes import schemas
from src.apps.disputes.service import DisputeService
from src.core import constants, dependencies

router = APIRouter(prefix="/disputes", tags=["Диспуты"])


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить данные диспута по ID.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.GET_DISPUTE])
        ),
    ],
)
async def get_dispute_by_id_route(
    id: int,
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить данные диспута по ID.

    Требуется разрешение: `получить диспут`.
    """
    return await DisputeService.get_by_id(session=session, id=id)


@router.get(
    "",
    summary="Получить список диспутов.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.GET_DISPUTE])
        ),
    ],
)
async def get_disputes_by_admin_route(
    query_params: schemas.DisputePaginationSchema = Query(),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить список диспутов.

    Требуется разрешение: `получить свой диспут`.
    """
    return await DisputeService.get_all(session=session, query_params=query_params)
