"""Модуль роутера для работы с пользователями."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.model import UserModel
from src.apps.users.schemas import pay_schemas
from src.apps.users.service import UserService
from src.core import constants, dependencies

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


# MARK: Patch
@router.patch(
    "/request-pay-in",
    summary="Запросить пополнение средств",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.REQUEST_PAY_IN]
            )
        ),
    ],
)
async def request_pay_in_route(
    body: pay_schemas.RequestPayInSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
) -> pay_schemas.ResponsePayInSchema:
    """
    Запросить пополнение средств как трейдер.

    Требуется разрешение: `запросить пополнение средств как трейдер`.
    """
    return await UserService.request_pay_in(
        session=session,
        user=user,
        amount=body.amount,
    )


@router.patch(
    "/confirm-pay-in",
    summary="Подтвердить пополнение средств",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.CONFIRM_PAY_IN]
            )
        ),
    ],
)
async def confirm_pay_in_route(
    body: pay_schemas.ConfirmPayInSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
) -> None:
    """
    Подтвердить пополнение средств как трейдер.

    Требуется разрешение: `подтвердить пополнение средств как трейдер`.
    """
    return await UserService.confirm_pay_in(
        session=session,
        user=user,
        transaction_hash=body.transaction_hash,
    )


@router.patch(
    "/request-pay-out",
    summary="Запросить вывод средств",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.REQUEST_PAY_OUT]
            )
        ),
    ],
)
async def request_pay_out_route(
    body: pay_schemas.RequestPayOutSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
) -> pay_schemas.ResponsePayOutSchema:
    """
    Запросить вывод средств как трейдер.

    Требуется разрешение: `запросить вывод средств как трейдер`.
    """
    return await UserService.request_pay_out(
        session=session,
        user=user,
        data=body,
    )
