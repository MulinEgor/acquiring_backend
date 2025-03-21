"""Модуль для роутера трейдеров."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.traders import schemas
from src.apps.traders.service import TraderService
from src.apps.users.model import UserModel
from src.core import constants, dependencies

router = APIRouter(
    prefix="/traders",
    tags=["Трейдеры"],
)


# MARK: Pay in
@router.post(
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


@router.post(
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


# MARK: Pay out
@router.post(
    "/request-pay-out",
    summary="Запросить вывод средств как трейдер",
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_pay_out(
    body: schemas.RequestPayOutSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.REQUEST_PAY_OUT_TRADER]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
) -> None:
    """
    Запросить вывод средств как трейдер.

    Требуется разрешение: `запросить вывод средств как трейдер`.
    """
    return await TraderService.request_pay_out(
        session=session,
        user=user,
        data=body,
    )
