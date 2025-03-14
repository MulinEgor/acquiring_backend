"""Модуль для моделей, связывающих роли и разрешения."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class RolesPermissionsModel(Base):
    """Модель для связи ролей и разрешений."""

    __tablename__ = "roles_permissions"

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("roles.id"),
        primary_key=True,
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        ForeignKey("permissions.id"),
        primary_key=True,
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

    role: Mapped["RoleModel"] = relationship(
        back_populates="roles_permissions",
        foreign_keys=[role_id],
        lazy="selectin",
    )
    permission: Mapped["PermissionModel"] = relationship(
        back_populates="roles_permissions",
        foreign_keys=[permission_id],
        lazy="selectin",
    )
