"""Модуль для роутера диспутов."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.disputes import schemas
from src.apps.disputes.service import DisputeService
from src.apps.users.model import UserModel
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
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.CREATE_DISPUTE])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    return await DisputeService.create(session=session, data=data, merchant_db=user)


# MARK: Get
@router.get(
    "/{id}",
    summary="Получить данные диспута по ID.",
    status_code=status.HTTP_200_OK,
)
async def get_dispute_by_id_route(
    id: int,
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.GET_MY_DISPUTE])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить данные диспута по ID.

    Требуется разрешение: `получить свой диспут`.
    """
    return await DisputeService.get_by_id(session=session, id=id, user_id=user.id)


@router.get(
    "",
    summary="Получить список диспутов.",
    status_code=status.HTTP_200_OK,
)
async def get_disputes_route(
    query_params: schemas.DisputePaginationSchema = Query(),
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions([constants.PermissionEnum.GET_MY_DISPUTE])
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Получить список диспутов.

    Требуется разрешение: `получить свой диспут`.
    """
    return await DisputeService.get_all(
        session=session,
        query_params=schemas.DisputeSupportPaginationSchema(
            user_id=user.id,
            **query_params.model_dump(exclude_unset=True),
        ),
    )


# MARK: Put
@router.put(
    "/{id}",
    summary="Обновить диспут по ID.",
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_dispute_by_id_route(
    id: int,
    data: schemas.DisputeUpdateSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.UPDATE_MY_DISPUTE]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
):
    """
    Обновить диспут по ID.

    Требуется разрешение: `обновить свой диспут`.
    """

    return await DisputeService.update(
        session=session, id=id, data=data, trader_db=user
    )
