"""Роуты для пополнения и вывода средств мерчанта."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.merchant import schemas
from src.apps.merchant.service import MerchantService
from src.apps.users.model import UserModel
from src.core import constants, dependencies

router = APIRouter(
    prefix="/merchant",
    tags=["Мерчант"],
)


# MARK: Pay in
@router.post(
    "/request-pay-in",
    summary="Запросить пополнение средств как мерчант",
)
async def request_pay_in_route(
    body: schemas.MerchantPayInRequestSchema,
    user: UserModel = Depends(dependencies.get_current_user),
    _=Depends(
        dependencies.check_user_permissions(
            [constants.PermissionEnum.REQUEST_PAY_IN_MERCHANT]
        )
    ),
    session: AsyncSession = Depends(dependencies.get_session),
) -> schemas.MerchantPayInResponseCardSchema | schemas.MerchantPayInResponseSbpSchema:
    """
    Запросить пополнение средств как мерчант.

    Требуется разрешение: `запросить пополнение средств как мерчант`.
    """
    return await MerchantService.request_pay_in(session=session, user=user, schema=body)
