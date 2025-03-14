"""Модулья для SQLAlchemy моделей для работы с ролями."""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import TIMESTAMP, UUID
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.roles_permissions.models import RolesPermissions


class RoleEnum(str, Enum):
    MERCHANT = "merchant"
    TRADER = "trader"
    SUPPORT = "support"
    ADMIN = "admin"


class RoleModel(Base):
    """Модель для работы с ролями."""

    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        default=uuid.uuid4,
        primary_key=True,
        comment="ID роли.",
    )
    name: Mapped[RoleEnum] = mapped_column(
        SQLAlchemyEnum(RoleEnum),
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

    roles_permissions: Mapped[list[RolesPermissions]] = relationship(
        back_populates="role",
    )
    users: Mapped[list["UserModel"]] = relationship(
        back_populates="role",
    )
