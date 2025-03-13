"""Модуль конфигурации базы данных."""

from sqlalchemy import MetaData, NullPool
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.settings import settings

DB_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}


class Base(AsyncAttrs, DeclarativeBase):
    """
    Основной класс для всех моделей базы данных.
    Наследуется от sqlalchemy.orm.DeclarativeBase
    и sqlalchemy.ext.asyncio.AsyncAttrs для обеспечения
    await на "лениво" загружаемых объектах.
    """

    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)


engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)
