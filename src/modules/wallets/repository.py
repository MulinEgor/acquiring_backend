"""Модуль для работы с репозиториями кошельков."""

from typing import Tuple

from sqlalchemy import Select, select

from src.core.base.repository import BaseRepository
from src.modules.wallets import schemas
from src.modules.wallets.models import WalletModel


class WalletRepository(BaseRepository[WalletModel, schemas.WalletCreateSchema, any]):
    """Репозиторий для работы с кошельками."""

    model = WalletModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.WalletPaginationSchema,
    ) -> Select[Tuple[WalletModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка кошельков.

        Args:
            query_params (WalletPaginationSchema): параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(WalletModel)

        # Фильтрация по адресу.
        if query_params.address:
            stmt = stmt.where(WalletModel.address == query_params.address)

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(WalletModel.created_at.desc())
        else:
            stmt = stmt.order_by(WalletModel.created_at)

        return stmt
