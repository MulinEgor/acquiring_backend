import datetime

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.permissions.model import PermissionModel
from src.apps.users.model import UserModel
from src.core.database import Base


class UsersPermissionsModel(Base):
    """Модель для связи пользователей и разрешений."""

    __tablename__ = "users_permissions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
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
