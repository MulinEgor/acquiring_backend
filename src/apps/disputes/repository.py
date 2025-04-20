from typing import Tuple

from sqlalchemy import Select, or_, select

from src.apps.disputes import schemas
from src.apps.disputes.model import DisputeModel
from src.apps.transactions.model import TransactionModel
from src.lib.base.repository import BaseRepository


class DisputeRepository(
    BaseRepository[
        DisputeModel, schemas.DisputeCreateSchema, schemas.DisputeSupportUpdateSchema
    ]
):
    """Репозиторий для работы с диспутами."""

    model = DisputeModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.DisputeSupportPaginationSchema,
    ) -> Select[Tuple[DisputeModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка диспутов.

        Args:
            query_params (DisputeSupportPaginationSchema): параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(cls.model)

        # Фильтрация по текстовым полям.
        field_to_value = {
            cls.model.transaction_id: query_params.transaction_id,
            cls.model.winner_id: query_params.winner_id,
        }
        for field, value in field_to_value.items():
            if value:
                stmt = stmt.where(field == value)

        if query_params.description:
            stmt = stmt.where(
                cls.model.description.ilike(f"%{query_params.description}%")
            )

        if query_params.user_id:
            stmt = stmt.join(TransactionModel).where(
                or_(
                    TransactionModel.merchant_id == query_params.user_id,
                    TransactionModel.trader_id == query_params.user_id,
                )
            )

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(cls.model.created_at.desc())
        else:
            stmt = stmt.order_by(cls.model.created_at)

        return stmt
