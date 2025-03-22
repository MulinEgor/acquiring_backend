"""Модуль для репозиториев трейдеров."""

import select

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

        stmt = (
            select(cls.model, RequisiteModel)
            .join(
                cls.model.requisites,
                cls.model.trader_transactions,
                RequisiteModel.payment_method == payment_method,
            )
            .where(
                cls.model.trader_transactions.all_(
                    TransactionModel.status != TransactionStatusEnum.PENDING
                )
            )
        )
        result = await session.execute(stmt)

        return result.first()
