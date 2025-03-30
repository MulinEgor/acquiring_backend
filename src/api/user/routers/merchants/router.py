"""Роуты для пополнения и вывода средств мерчанта."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.merchants import schemas
from src.apps.merchants.service import MerchantService
from src.apps.users.model import UserModel
from src.core import constants, dependencies

router = APIRouter(
    prefix="/merchant-clients",
    tags=["Клиенты мерчантов"],
)


# MARK: Pay in
@router.post(
    "/request-pay-in",
    summary="Запросить пополнение средств как клиент мерчанта",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.REQUEST_PAY_IN_CLIENT]
            )
        ),
    ],
)
async def request_pay_in_route(
    body: schemas.MerchantPayInRequestSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
) -> schemas.MerchantPayInResponseCardSchema | schemas.MerchantPayInResponseSBPSchema:
    """
    Запросить пополнение средств как клиент мерчанта.

    Требуется разрешение: `запросить пополнение средств как клиент мерчанта`.
    """
    return await MerchantService.request_pay_in(session=session, user=user, schema=body)


# MARK: Pay out
@router.post(
    "/request-pay-out",
    summary="Запросить вывод средств как клиент мерчанта",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions(
                [constants.PermissionEnum.REQUEST_PAY_OUT_CLIENT]
            )
        ),
    ],
)
async def request_pay_out_route(
    body: schemas.MerchantPayOutRequestSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    session: AsyncSession = Depends(dependencies.get_session),
) -> None:
    """
    Запросить вывод средств как клиент мерчанта.

    Требуется разрешение: `запросить вывод средств как клиент мерчанта`.
    """
    return await MerchantService.request_pay_out(
        session=session, merchant_db=user, schema=body
    )
