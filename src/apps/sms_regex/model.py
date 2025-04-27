from datetime import datetime, timezone

from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class SmsRegexModel(Base):
    __tablename__ = "sms_regex"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    sender: Mapped[str] = mapped_column(unique=True)
    regex: Mapped[str] = mapped_column()
    is_card: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
