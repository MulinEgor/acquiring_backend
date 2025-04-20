from datetime import datetime, timedelta, timezone
from enum import StrEnum

from sqlalchemy import ARRAY, TIMESTAMP, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core import constants
from src.core.database import Base


class DisputeStatusEnum(StrEnum):
    PENDING = "в процессе рассмотрения"
    CLOSED = "закрыт"


class DisputeModel(Base):
    __tablename__ = "disputes"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    description: Mapped[str] = mapped_column(String(length=255))
    image_urls: Mapped[list[str]] = mapped_column(ARRAY(String))
    status: Mapped[DisputeStatusEnum] = mapped_column(
        Enum(DisputeStatusEnum),
        default=DisputeStatusEnum.PENDING,
    )
    winner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc)
        + timedelta(seconds=constants.PENDING_DISPUTE_TIMEOUT),
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )

    transaction: Mapped["TransactionModel"] = relationship(
        back_populates="dispute",
        foreign_keys=[transaction_id],
        uselist=False,
    )
    winner: Mapped["UserModel"] = relationship(
        back_populates="disputes",
        foreign_keys=[winner_id],
    )
