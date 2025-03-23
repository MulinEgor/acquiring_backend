"""Модуль для репозиториев трейдеров."""

from sqlalchemy import and_, not_, or_, select
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
    async def get_by_payment_method_and_amount(
        cls,
        session: AsyncSession,
        payment_method: TransactionPaymentMethodEnum,
        amount: int,
    ) -> tuple[UserModel, RequisiteModel]:
        """
        Получить трейдера по методу оплаты,
        у которого нет транзакций в процессе обработки.

        Args:
            session: Сессия для работы с БД.
            payment_method: Метод оплаты.
            amount: Сумма транзакции.

        Returns:
            tuple[UserModel, RequisiteModel]: Тренер и его реквизиты.

        Raises:
            NotFoundException: Тренер с таким методом оплаты не найден.
        """

        # Определение условия для фильтрации по методу оплаты
        if payment_method == TransactionPaymentMethodEnum.CARD:
            payment_method_stmt = not_(RequisiteModel.card_number.is_(None))
        else:
            payment_method_stmt = not_(
                or_(
                    RequisiteModel.phone_number.is_(None),
                    RequisiteModel.bank_name.is_(None),
                )
            )

        # Определение условия для фильтрации по реквизитам,
        #   которые не находятся в процессе обработки
        requisite_not_pending_stm = RequisiteModel.id.notin_(
            select(TransactionModel.requisite_id).where(
                TransactionModel.status == TransactionStatusEnum.PENDING.value
            )
        )

        # Определение условий для фильтрации по трейдеру
        trader_checks = [
            cls.model.is_active,
            cls.model.balance - cls.model.amount_frozen >= amount,
        ]

        # Определение условий для фильтрации по сумме транзакции,
        #   относительно ограничений реквизита.
        requisite_amount_checks = [
            or_(
                RequisiteModel.min_amount.is_(None),
                amount >= RequisiteModel.min_amount,
            ),
            or_(
                RequisiteModel.max_amount.is_(None),
                amount <= RequisiteModel.max_amount,
            ),
        ]

        stmt = (
            select(cls.model, RequisiteModel)
            .outerjoin(cls.model.trader_transactions)
            .where(
                and_(
                    payment_method_stmt,
                    requisite_not_pending_stm,
                    *trader_checks,
                    *requisite_amount_checks,
                )
            )
        )
        result = await session.execute(stmt)

        return result.first()
