"""Модуль для моделей транзакций на блокчейне."""

import uuid
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import TIMESTAMP, UUID, ForeignKey, Integer, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants
from src.core.database import Base


class StatusEnum(str, Enum):
    """Статус транзакции на блокчейне."""

    PENDING = "в процессе обработки"
    CONFIRMED = "подтверждена"
    FAILED = "не удачна"


class TypeEnum(str, Enum):
    """Тип транзакции на блокчейне."""

    PAY_IN = "входящая"
    PAY_OUT = "исходящая"


class BlockchainTransactionModel(Base):
    """Модель транзакции на блокчейне."""

    __tablename__ = "blockchain_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column()
    type: Mapped[TypeEnum] = mapped_column(SQLAlchemyEnum(TypeEnum))
    from_address: Mapped[str] = mapped_column(String(42), nullable=True)
    to_address: Mapped[str] = mapped_column(String(42))
    status: Mapped[StatusEnum] = mapped_column(
        SQLAlchemyEnum(StatusEnum), default=StatusEnum.PENDING
    )
    hash: Mapped[str] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.now)
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=lambda: datetime.now()
        + timedelta(seconds=constants.PENDING_BLOCKCHAIN_TRANSACTION_TIMEOUT),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.now, onupdate=datetime.now
    )

    user: Mapped["UserModel"] = relationship(back_populates="blockchain_transactions")
