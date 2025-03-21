"""Модуль для SQLAlchemy моделей реквизитов."""

from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class RequisiteModel(Base):
    """SQLAlchemy модель реквизитов."""

    __tablename__ = "requisites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    full_name: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column(nullable=True)
    bank_name: Mapped[str] = mapped_column(nullable=True)
    card_number: Mapped[str] = mapped_column(nullable=True)
    min_amount: Mapped[int] = mapped_column(nullable=True)
    max_amount: Mapped[int] = mapped_column(nullable=True)
    max_daily_amount: Mapped[int] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    user: Mapped["UserModel"] = relationship(back_populates="requisites")
