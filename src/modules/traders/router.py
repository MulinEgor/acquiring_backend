"""Модуль для роутера трейдеров."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import constants, dependencies
from src.modules.traders import schemas
from src.modules.traders.service import TraderService
from src.modules.users.models import UserModel

traders_router = APIRouter(
    prefix="/traders",
    tags=["Трейдеры"],
)


# MARK: Pay in
@traders_router.post(
    "/request-pay-in",
    summary="Запросить пополнение средств как трейдер",
)
async def request_pay_in(
    body: schemas.RequestPayInSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.REQUEST_PAY_IN_TRADER]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
) -> schemas.ResponsePayInSchema:
    """
    Запросить пополнение средств как трейдер.

    Требуется разрешение: `запросить пополнение средств как трейдер`.
    """
    return await TraderService.request_pay_in(
        session=session,
        user=user,
        amount=body.amount,
    )


@traders_router.post(
    "/confirm-pay-in",
    summary="Подтвердить пополнение средств как трейдер",
    status_code=status.HTTP_202_ACCEPTED,
)
async def confirm_pay_in(
    body: schemas.ConfirmPayInSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.CONFIRM_PAY_IN_TRADER]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
) -> None:
    """
    Подтвердить пополнение средств как трейдер.

    Требуется разрешение: `подтвердить пополнение средств как трейдер`.
    """
    return await TraderService.confirm_pay_in(
        session=session,
        user=user,
        transaction_hash=body.transaction_hash,
    )
