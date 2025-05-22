from typing import Generic, TypeVar

from loguru import logger
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import src.libs.base.types as types
from src.core import exceptions
from src.libs.base.repository import BaseRepository


class BaseService(
    Generic[
        types.ModelType,
        types.CreateSchemaType,
        types.GetSchemaType,
        types.PaginationSchemaType,
        types.GetListSchemaType,
        types.UpdateSchemaType,
    ],
):
    """
    Основной класс интерфейсов для сервисов, выполняющих CRUD операции.

    Args:
        repository: Репозиторий для работы с моделью.
    """

    repository: BaseRepository
    conflict_exception_message, conflict_exception_code = (
        "Возник конфликт при создании данных.",
        1001,
    )
    not_found_exception_message, not_found_exception_code = (
        "Данные не найдены.",
        1002,
    )

    # MARK: Utils
    @classmethod
    async def _get_schema_class_by_type(cls, type_var: TypeVar) -> type[BaseModel]:
        """
        Получить класс схемы по типу.

        Args:
            type_var (TypeVar): Тип схемы.

        Returns:
            type[BaseModel]: Класс схемы.
        """

        # Получаем оригинальные базовые классы (с дженерик параметрами)
        orig_bases = cls.__orig_bases__[0]

        # Получаем индекс нужного типа в списке параметров
        type_args = orig_bases.__args__
        type_index = next(
            i for i, arg in enumerate(BaseService.__parameters__) if arg == type_var
        )

        return type_args[type_index]

    # MARK: Create
    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: types.CreateSchemaType,
    ) -> types.GetSchemaType:
        """
        Создать объект в БД.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            data (CreateSchemaType): Данные для создания объекта.

        Returns:
            GetSchemaType: Добавленный объект.

        Raises:
            ConflictException: Конфликт при создании.
        """

        logger.opt(depth=1).info("Создание объекта: {}", data)

        try:
            # Добавление объекта в БД
            obj_db = await cls.repository.create(
                session=session,
                obj_in=data,
            )
            await session.commit()

            schema_class = await cls._get_schema_class_by_type(types.GetSchemaType)

            return schema_class.model_validate(obj_db)

        except IntegrityError as ex:
            raise exceptions.ConflictException(
                message=cls.conflict_exception_message,
                code=cls.conflict_exception_code,
                exc=ex,
            )

    # MARK: Get
    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        id: int,
        user_id: int | None = None,
    ) -> types.GetSchemaType:
        """
        Поиск объекта по ID.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            id (int): ID объекта.
            user_id (int | None): ID пользователя.
        Returns:
            GetSchemaType: Найденный объект.

        Raises:
            NotFoundException: Объект не найден.
        """

        logger.opt(depth=1).info("Поиск объекта по ID: {}", id)

        # Поиск объекта в БД
        obj_db = await cls.repository.get_one_or_none(session=session, id=id)

        if obj_db is None or (user_id and obj_db.user_id != user_id):
            raise exceptions.NotFoundException(message=cls.not_found_exception_message)

        schema_class = await cls._get_schema_class_by_type(types.GetSchemaType)
        return schema_class.model_validate(obj_db)

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        query_params: types.PaginationSchemaType,
        user_id: int | None = None,
    ) -> types.GetListSchemaType:
        """
        Получить список объектов и их общее количество
        с фильтрацией по query параметрам, отличным от None.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            query_params (GetQuerySchemaType): Query параметры для фильтрации.
            user_id (int | None): Идентификатор пользователя.

        Returns:
            GetListSchemaType: список объектов и их общее количество.

        Raises:
            NotFoundException: Объекты не найдены.
        """

        logger.opt(depth=1).info(
            "Получение списка объектов с параметрами: {}",
            query_params.model_dump(),
        )

        base_stmt = await cls.repository.get_stmt_by_query(
            query_params=query_params,
        )
        if user_id:
            base_stmt = base_stmt.where(cls.repository.model.user_id == user_id)

        objects_db = await cls.repository.get_all_with_pagination_from_stmt(
            session=session,
            limit=query_params.limit,
            offset=query_params.offset,
            stmt=base_stmt,
        )

        if not objects_db:
            raise exceptions.NotFoundException(message=cls.not_found_exception_message)

        objects_count = await cls.repository.count_subquery(
            session=session,
            stmt=base_stmt,
        )

        # Получаем класс схемы для одного объекта
        item_schema_class = await cls._get_schema_class_by_type(types.GetSchemaType)
        # Преобразуем каждый объект в схему
        objects_schema = [item_schema_class.model_validate(obj) for obj in objects_db]

        # Получаем класс схемы для списка и создаем его экземпляр
        list_schema_class = await cls._get_schema_class_by_type(types.GetListSchemaType)

        return list_schema_class(
            count=objects_count,
            data=objects_schema,
        )

    # MARK: Update
    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        id: int,
        data: types.UpdateSchemaType,
    ) -> types.GetSchemaType:
        """
        Обновить данные объекта.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            id (int): ID объекта.
            data (UpdateSchemaType): Данные для обновления объекта.

        Returns:
            GetSchemaType: Обновленный объект.

        Raises:
            NotFoundException: Объект не найден.
            ConflictException: Объект с такими данными уже существует.
        """

        logger.opt(depth=1).info("Обновление объекта с ID: {}", id)

        # Поиск объекта в БД
        await cls.get_by_id(session=session, id=id)

        # Обновление объекта в БД
        try:
            updated_obj = await cls.repository.update(
                cls.repository.model.id == id,
                session=session,
                obj_in=data,
            )
            await session.commit()

        except IntegrityError as ex:
            raise exceptions.ConflictException(
                message=cls.conflict_exception_message,
                code=cls.conflict_exception_code,
                exc=ex,
            )

        schema_class = await cls._get_schema_class_by_type(types.GetSchemaType)

        return schema_class.model_validate(updated_obj)

    # MARK: Delete
    @classmethod
    async def delete(
        cls,
        session: AsyncSession,
        id: int,
    ):
        """
        Удалить объект.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            id (int): ID объекта.

        Raises:
            NotFoundException: Объект не найден.
        """

        logger.opt(depth=1).info("Удаление объекта с ID: {}", id)

        # Поиск объекта в БД
        await cls.get_by_id(session=session, id=id)

        # Удаление объекта из БД
        await cls.repository.delete(
            id=id,
            session=session,
        )
        await session.commit()
