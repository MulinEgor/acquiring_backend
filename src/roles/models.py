"""Модулья для SQLAlchemy моделей для работы с ролями."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.roles_permissions.models import RolesPermissionsModel


class RoleModel(Base):
    """Модель для работы с ролями."""

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        default=uuid.uuid4,
        primary_key=True,
        comment="ID роли.",
    )
    name: Mapped[str] = mapped_column(
        unique=True,
        comment="Название роли.",
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

    roles_permissions: Mapped[list[RolesPermissionsModel]] = relationship(
        back_populates="role",
    )
    users: Mapped[list["UserModel"]] = relationship(
        back_populates="role",
    )
