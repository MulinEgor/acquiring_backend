"""Модуль для роутера трейдеров."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.traders.service import TraderService
from src.apps.users.model import UserModel
from src.apps.users.service import UserService
from src.core import constants, dependencies

router = APIRouter(
    prefix="/traders",
    tags=["Трейдер"],
)


# MARK: Patch
@router.patch(
    "/confirm-merchant-pay-in/{transaction_id}",
    summary="Подтвердить пополнение средств мерчантом",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.CONFIRM_MERCHANT_PAY_IN_TRADER]
            )
        ),
    ],
)
async def confirm_merchant_pay_in_route(
    transaction_id: int,
    user: UserModel = Depends(dependencies.get_current_user),
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


@router.patch(
    "/start",
    summary="Начать работу",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.START_WORKING_TRADER]
            )
        ),
    ],
)
async def start_work_route(
    user: UserModel = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
) -> None:
    """
    Начать работу.

    Требуется разрешение: `начать работу как трейдер`.
    """
    return await UserService.set_is_active(
        session=session,
        user=user,
        is_active=True,
    )


@router.patch(
    "/stop",
    summary="Остановить работу",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.STOP_WORKING_TRADER]
            )
        ),
    ],
)
async def stop_work_route(
    user: UserModel = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
) -> None:
    """
    Остановить работу.

    Требуется разрешение: `остановить работу как трейдер`.
    """
    return await UserService.set_is_active(
        session=session,
        user=user,
        is_active=False,
    )
