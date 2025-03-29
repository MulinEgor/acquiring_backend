"""Модуль для SQLAlchemy моделей диспутов."""

from datetime import datetime

from sqlalchemy import ARRAY, TIMESTAMP, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class DisputeModel(Base):
    """Модель диспута."""

    __tablename__ = "disputes"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    description: Mapped[str] = mapped_column(String(length=255))
    image_urls: Mapped[list[str]] = mapped_column(ARRAY(String))
    winner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
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
