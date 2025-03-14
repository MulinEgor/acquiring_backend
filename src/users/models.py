"""Модуль для SQLAlchemy моделей пользователей."""

import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src import constants
from src.database import Base


class UserModel(Base):
    """SQLAlchemy модель пользователя."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4,
        primary_key=True,
        comment="Уникальный идентификатор пользователя.",
    )
    email: Mapped[str] = mapped_column(
        unique=True,
        comment="Электронная почта пользователя.",
    )
    hashed_password: Mapped[str] = mapped_column(
        comment="Хэшированный пароль пользователя.",
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("roles.id"),
        comment="ID роли пользователя.",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=constants.CURRENT_TIMESTAMP_UTC,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=constants.CURRENT_TIMESTAMP_UTC,
        onupdate=constants.CURRENT_TIMESTAMP_UTC,
    )

    role: Mapped["RoleModel"] = relationship(
        back_populates="users",
        lazy="selectin",
    )
