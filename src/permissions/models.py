"""Модулья для SQLAlchemy моделей для работы с разрешениями."""

from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.users_permissions.models import UsersPermissionsModel


class PermissionModel(Base):
    """Модель для работы с разрешениями."""

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(
        autoincrement=True,
        primary_key=True,
        comment="ID разрешения.",
    )
    name: Mapped[str] = mapped_column(
        unique=True,
        comment="Название разрешения.",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    users_permissions: Mapped[list[UsersPermissionsModel]] = relationship(
        back_populates="permission",
        lazy="selectin",
        cascade="all, delete",
    )
