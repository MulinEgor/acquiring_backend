"""Модуль для репозиториев трейдеров."""

from sqlalchemy import and_, exists, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.requisites.model import RequisiteModel
from src.apps.transactions.model import (
    TransactionModel,
    TransactionPaymentMethodEnum,
    TransactionStatusEnum,
)
from src.apps.users import schemas as user_schemas
from src.apps.users.model import UserModel
from src.lib.base.repository import BaseRepository


class TraderRepository(
    BaseRepository[
        UserModel,
        user_schemas.UserCreateSchema,
        user_schemas.UserUpdateSchema,
    ],
):
    """
    Репозиторий для работы с моделью UserModel, а именно с трейдерами.
    Наследуется от базового репозитория.
    """

    model = UserModel

    @classmethod
    async def get_by_payment_method(
        cls,
        session: AsyncSession,
        payment_method: TransactionPaymentMethodEnum,
    ) -> tuple[UserModel, RequisiteModel]:
        """
        Получить трейдера по методу оплаты,
        у которого нет транзакций в процессе обработки.

        Args:
            session: Сессия для работы с БД.
            payment_method: Метод оплаты.

        Returns:
            tuple[UserModel, RequisiteModel]: Тренер и его реквизиты.

        Raises:
            NotFoundException: Тренер с таким методом оплаты не найден.
        """

        if payment_method == TransactionPaymentMethodEnum.CARD:
            requisite_join_condition = not_(RequisiteModel.card_number.is_(None))
        else:
            requisite_join_condition = not_(
                or_(
                    RequisiteModel.phone_number.is_(None),
                    RequisiteModel.bank_name.is_(None),
                )
            )

        subquery = (
            select(TransactionModel).where(
                and_(
                    TransactionModel.trader_id == cls.model.id,
                    TransactionModel.status == TransactionStatusEnum.PENDING.value,
                )
            )
        ).correlate(None)

        stmt = (
            select(cls.model, RequisiteModel)
            .outerjoin(cls.model.trader_transactions)
            .where(and_(requisite_join_condition, ~exists(subquery)))
        )
        result = await session.execute(stmt)

        return result.first()
