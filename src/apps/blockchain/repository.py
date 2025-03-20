"""Модуль для репозитория транзакций на блокчейне."""

from typing import Tuple

from sqlalchemy import Select, select

from src.apps.blockchain import schemas
from src.apps.blockchain.models import BlockchainTransactionModel
from src.lib.base.repository import BaseRepository


class BlockchainTransactionRepository(
    BaseRepository[BlockchainTransactionModel, schemas.TransactionCreateSchema, any]
):
    """Репозиторий транзакций на блокчейне."""

    model = BlockchainTransactionModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.TransactionPaginationSchema,
    ) -> Select[Tuple[BlockchainTransactionModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка разрешений.

        Args:
            query_params (PermissionPaginationSchema): параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(BlockchainTransactionModel)

        # Фильтрация по текстовым полям.
        field_to_value = {
            cls.model.hash: query_params.hash,
            cls.model.from_address: query_params.from_address,
            cls.model.to_address: query_params.to_address,
            cls.model.type: query_params.type,
            cls.model.status: query_params.status,
        }
        for field, value in field_to_value.items():
            if value:
                stmt = stmt.where(field == value)

        # Фильтрация по числовым полям.
        if query_params.min_amount:
            stmt = stmt.where(cls.model.amount >= query_params.min_amount)
        if query_params.max_amount:
            stmt = stmt.where(cls.model.amount <= query_params.max_amount)

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(cls.model.created_at.desc())
        else:
            stmt = stmt.order_by(cls.model.created_at)

        return stmt
