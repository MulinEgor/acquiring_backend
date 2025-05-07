from typing import Tuple

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.notifications import schemas
from src.apps.notifications.model import NotificationModel
from src.libs.base.repository import BaseRepository


class NotificationRepository(
    BaseRepository[
        NotificationModel,
        schemas.NotificationCreateSchema,
        schemas.NotificationUpdateSchema,
    ],
):
    """Репозиторий для работы с уведомлениями."""

    model = NotificationModel

    @classmethod
    async def get_stmt_by_query(
        cls,
        query_params: schemas.NotificationPaginationSchema,
    ) -> Select[Tuple[NotificationModel]]:
        """
        Создать подготовленное выражение для запроса в БД,
        применив основные query параметры без учета пагинации,
        для получения списка уведомлений.

        Args:
            query_params (NotificationPaginationSchema): параметры для запроса.

        Returns:
            stmt: Подготовленное выражение для запроса в БД.
        """

        stmt = select(NotificationModel)

        # Фильтрация по текстовым полям.
        if query_params.user_id:
            stmt = stmt.where(NotificationModel.user_id == query_params.user_id)

        if query_params.message:
            stmt = stmt.where(
                NotificationModel.message.ilike(f"%{query_params.message}%")
            )

        # Сортировка по дате создания.
        if not query_params.asc:
            stmt = stmt.order_by(NotificationModel.created_at.desc())
        else:
            stmt = stmt.order_by(NotificationModel.created_at)

        return stmt

    @classmethod
    async def read_all(
        cls,
        session: AsyncSession,
        notification_ids: list[int],
        user_id: int,
    ) -> None:
        """
        Прочитать все уведомления.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            notification_ids (list[int]): Список идентификаторов уведомлений.
            user_id (int): Идентификатор пользователя.
        """

        stmt = (
            update(cls.model)
            .where(cls.model.id.in_(notification_ids))
            .where(cls.model.user_id == user_id)
            .values({"is_read": True})
        )

        await session.execute(stmt)
        await session.commit()
