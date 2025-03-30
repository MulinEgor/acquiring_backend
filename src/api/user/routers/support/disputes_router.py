"""Модуль для роутера диспутов для суппорта."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.disputes import schemas
from src.apps.disputes.service import DisputeService
from src.core import constants, dependencies

router = APIRouter(prefix="/support/disputes", tags=["Диспуты для суппорта"])


# MARK: Get
@router.put(
    "/{id}",
    summary="Обновить диспут по ID.",
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_dispute_by_id_route(
    id: int,
    data: schemas.DisputeSupportUpdateSchema,
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.GET_DISPUTE])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Обновить диспут по ID.

    Требуется разрешение: `обновить диспут`.
    """
    return await DisputeService.update_by_support(session=session, id=id, data=data)
