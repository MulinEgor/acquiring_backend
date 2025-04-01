"""Модуль для репозитория для работы с реквизитами."""

from typing import Tuple

from sqlalchemy import Select, select

from src.apps.requisites import schemas
from src.apps.requisites.model import RequisiteModel
from src.lib.base.repository import BaseRepository


class RequisiteRepository(
    BaseRepository[
        RequisiteModel,
        schemas.RequisiteCreateAdminSchema,
        schemas.RequisiteUpdateAdminSchema,
    ],
):
    """Репозиторий для работы с реквизитами."""

    model = RequisiteModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.RequisitePaginationSchema
        | schemas.RequisitePaginationAdminSchema,
    ) -> Select[Tuple[RequisiteModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка реквизитов.

        Args:
            query_params (RequisitePaginationSchema | RequisitePaginationAdminSchema):
                параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(cls.model)

        # Фильтрация по текствым полям.
        field_to_value = {
            cls.model.full_name: query_params.full_name,
            cls.model.phone_number: query_params.phone_number,
            cls.model.bank_name: query_params.bank_name,
            cls.model.card_number: query_params.card_number,
        }
        for field, value in field_to_value.items():
            if value:
                stmt = stmt.where(field.ilike(f"%{value}%"))

        # Фильтрация по ID пользователя для админа.
        if (
            isinstance(query_params, schemas.RequisitePaginationAdminSchema)
            and query_params.user_id is not None
        ):
            stmt = stmt.where(cls.model.user_id == query_params.user_id)

        # Фильрация по числовым полям.
        if query_params.min_amount is not None:
            stmt = stmt.where(cls.model.min_amount >= query_params.min_amount)
        if query_params.max_amount is not None:
            stmt = stmt.where(cls.model.max_amount <= query_params.max_amount)

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(cls.model.created_at.desc())
        else:
            stmt = stmt.order_by(cls.model.created_at)

        return stmt
