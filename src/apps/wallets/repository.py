"""Модуль для работы с репозиториями кошельков."""

from typing import Tuple

from sqlalchemy import Select, select

from src.apps.wallets import schemas
from src.apps.wallets.model import WalletModel
from src.lib.base.repository import BaseRepository


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

        # Фильтрация по текстовым полям.
        if query_params.address:
            stmt = stmt.where(WalletModel.address == query_params.address)

        if query_params.private_key:
            stmt = stmt.where(WalletModel.private_key == query_params.private_key)

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(WalletModel.created_at.desc())
        else:
            stmt = stmt.order_by(WalletModel.created_at)

        return stmt
