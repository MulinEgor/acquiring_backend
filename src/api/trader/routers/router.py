"""Модуль для роутера трейдеров."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.traders import schemas
from src.apps.traders.service import TraderService
from src.apps.users.model import UserModel
from src.core import constants, dependencies

router = APIRouter(
    prefix="/traders",
    tags=["Трейдер"],
)


# MARK: Patch
@router.patch(
    "/request-pay-in",
    summary="Запросить пополнение средств как трейдер",
)
async def request_pay_in_route(
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


@router.patch(
    "/confirm-pay-in",
    summary="Подтвердить пополнение средств как трейдер",
    status_code=status.HTTP_202_ACCEPTED,
)
async def confirm_pay_in_route(
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


@router.patch(
    "/request-pay-out",
    summary="Запросить вывод средств как трейдер",
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_pay_out_route(
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


@router.patch(
    "/confirm-merchant-pay-in/{transaction_id}",
    summary="Подтвердить пополнение средств мерчантом",
    status_code=status.HTTP_202_ACCEPTED,
)
async def confirm_merchant_pay_in_route(
    transaction_id: int,
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.CONFIRM_MERCHANT_PAY_IN_TRADER]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
) -> None:
    """
    Подтвердить пополнение средств мерчантом.

    Требуется разрешение: `подтвердить пополнение средств мерчантом`.
    """
    return await TraderService.confirm_merchant_pay_in(
        session=session,
        transaction_id=transaction_id,
        trader_db=user,
    )
