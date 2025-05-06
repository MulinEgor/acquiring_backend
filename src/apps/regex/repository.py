from typing import Tuple

from sqlalchemy import Select, select

from src.apps.regex import schemas
from src.apps.regex.model import RegexModel
from src.lib.base.repository import BaseRepository


class RegexRepository(
    BaseRepository[
        RegexModel,
        schemas.RegexCreateSchema,
        schemas.RegexUpdateSchema,
    ],
):
    model = RegexModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.RegexPaginationSchema,
    ) -> Select[Tuple[RegexModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка sms-regex.
        """

        stmt = select(cls.model)

        # Фильтрация по текстовым полям.
        text_filters = {
            cls.model.sender: query_params.sender,
            cls.model.regex: query_params.regex,
            cls.model.type: query_params.type,
        }
        for field, value in text_filters.items():
            if value:
                stmt = stmt.where(field.ilike(f"%{value}%"))

        # Фильтрация по типу.
        if query_params.is_card is not None:
            stmt = stmt.where(cls.model.is_card == query_params.is_card)

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(cls.model.created_at.desc())
        else:
            stmt = stmt.order_by(cls.model.created_at)

        return stmt
