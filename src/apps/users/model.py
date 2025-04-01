"""Модуль для SQLAlchemy моделей пользователей."""

from datetime import datetime

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.blockchain.model import BlockchainTransactionModel
from src.apps.disputes.model import DisputeModel
from src.apps.notifications.model import NotificationModel
from src.apps.requisites.model import RequisiteModel
from src.apps.transactions.model import TransactionModel
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
        default=False,
        comment="Применяется для трейдера, а именно находится ли он в работе.",
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
    requisites: Mapped[list[RequisiteModel]] = relationship(
        back_populates="user",
        lazy="selectin",
        cascade="all, delete",
    )
    blockchain_transactions: Mapped[list[BlockchainTransactionModel]] = relationship(
        back_populates="user",
    )
    trader_transactions: Mapped[list[TransactionModel]] = relationship(
        back_populates="trader",
        foreign_keys=[TransactionModel.trader_id],
    )
    merchant_transactions: Mapped[list[TransactionModel]] = relationship(
        back_populates="merchant",
        foreign_keys=[TransactionModel.merchant_id],
    )
    disputes: Mapped[list[DisputeModel]] = relationship(
        back_populates="winner",
        foreign_keys=[DisputeModel.winner_id],
    )
    notifications: Mapped[list[NotificationModel]] = relationship(
        back_populates="user",
        cascade="all, delete",
    )
