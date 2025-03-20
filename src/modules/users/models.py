"""Модуль для SQLAlchemy моделей пользователей."""

from datetime import datetime

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants
from src.core.database import Base


class UserModel(Base):
    """SQLAlchemy модель пользователя."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        autoincrement=True,
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
    balance: Mapped[int] = mapped_column(
        default=0,
        comment="Баланс пользователя.",
    )
    amount_frozen: Mapped[int] = mapped_column(
        default=0,
        comment="Замороженные средства пользователя.",
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment="Является ли аккаунт пользователя активным.",
    )
    is_2fa_enabled: Mapped[bool] = mapped_column(
        default=False,
        comment="Является ли 2FA включенным.",
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

    users_permissions: Mapped[list["UsersPermissionsModel"]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete",
    )
    blockchain_transactions: Mapped[list["BlockchainTransactionModel"]] = relationship(
        back_populates="user",
    )
