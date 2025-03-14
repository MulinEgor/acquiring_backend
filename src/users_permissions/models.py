"""Модуль для моделей SQLAlchemy для связи пользователей и разрешений."""

import datetime
import uuid

from sqlalchemy import TIMESTAMP, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class UsersPermissionsModel(Base):
    """Модель для связи пользователей и разрешений."""

    __tablename__ = "users_permissions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("users.id"),
        primary_key=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("permissions.id"),
        primary_key=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.datetime.now,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )

    user: Mapped["UserModel"] = relationship(
        back_populates="users_permissions",
        foreign_keys=[user_id],
        lazy="selectin",
    )
    permission: Mapped["PermissionModel"] = relationship(
        back_populates="users_permissions",
        foreign_keys=[permission_id],
        lazy="selectin",
    )
