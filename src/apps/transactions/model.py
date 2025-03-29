"""Модуль для SQLAlchemy моделей транзакций на платформе."""

from datetime import datetime, timedelta, timezone
from enum import Enum

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants
from src.core.database import Base


class TransactionStatusEnum(str, Enum):
    """Статус транзакции."""

    PENDING = "в процессе обработки"
    FAILED = "не удачна"
    CLOSED = "закрыта"
    DISPUTED = "в процессе рассмотрения"


class TransactionTypeEnum(str, Enum):
    """Тип транзакции."""

    PAY_IN = "входящая"
    PAY_OUT = "исходящая"


class TransactionPaymentMethodEnum(str, Enum):
    """Способ оплаты транзакции."""

    CARD = "карта"
    SBP = "сбп"


class TransactionModel(Base):
    """SQLAlchemy модель транзакций на платформе."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    merchant_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column()
    payment_method: Mapped[TransactionPaymentMethodEnum] = mapped_column(
        SQLAlchemyEnum(TransactionPaymentMethodEnum)
    )
    status: Mapped[TransactionStatusEnum] = mapped_column(
        SQLAlchemyEnum(TransactionStatusEnum), default=TransactionStatusEnum.PENDING
    )
    type: Mapped[TransactionTypeEnum] = mapped_column(
        SQLAlchemyEnum(TransactionTypeEnum)
    )
    trader_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    requisite_id: Mapped[int] = mapped_column(
        ForeignKey("requisites.id"), nullable=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc)
        + timedelta(seconds=constants.PENDING_TRANSACTION_TIMEOUT),
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

    merchant: Mapped["UserModel"] = relationship(
        back_populates="merchant_transactions",
        foreign_keys=[merchant_id],
    )
    trader: Mapped["UserModel"] = relationship(
        back_populates="trader_transactions",
        foreign_keys=[trader_id],
    )
    requisite: Mapped["RequisiteModel"] = relationship(
        back_populates="transactions",
        foreign_keys=[requisite_id],
    )
    dispute: Mapped["DisputeModel"] = relationship(
        back_populates="transaction",
        uselist=False,
    )
