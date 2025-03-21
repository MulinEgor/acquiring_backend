"""Модуль для репозитория для работы с транзакциями."""

from typing import Tuple

from sqlalchemy import Select, select

from src.apps.transactions import schemas
from src.apps.transactions.model import TransactionModel
from src.lib.base.repository import BaseRepository


class TransactionRepository(
    BaseRepository[
        TransactionModel,
        schemas.TransactionCreateSchema,
        schemas.TransactionUpdateSchema,
    ],
):
    """Репозиторий для работы с транзакциями."""

    model = TransactionModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.TransactionAdminPaginationSchema,
    ) -> Select[Tuple[TransactionModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка транзакций.

        Args:
            query_params (TransactionPaginationSchema):
                параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(TransactionModel)

        # Фильтрация по текствым и числовым полям.
        field_to_value = {
            cls.model.merchant_id: query_params.merchant_id,
            cls.model.payment_method: query_params.payment_method,
            cls.model.type: query_params.type,
            cls.model.trader_id: query_params.trader_id,
        }
        for field, value in field_to_value.items():
            if value:
                stmt = stmt.where(field == value)

        # Фильрация по минимальной и максимальной сумме.
        if query_params.min_amount is not None:
            stmt = stmt.where(cls.model.amount >= query_params.min_amount)
        if query_params.max_amount is not None:
            stmt = stmt.where(cls.model.amount <= query_params.max_amount)

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(cls.model.created_at.desc())
        else:
            stmt = stmt.order_by(cls.model.created_at)

        return stmt
