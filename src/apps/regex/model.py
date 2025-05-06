from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import TIMESTAMP
from sqlalchemy import Enum as SQAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class RegexType(Enum):
    PUSH = "push"
    SMS = "sms"


class RegexModel(Base):
    __tablename__ = "regex"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    sender: Mapped[str] = mapped_column(unique=True)
    regex: Mapped[str] = mapped_column()
    is_card: Mapped[bool] = mapped_column()
    type: Mapped[RegexType] = mapped_column(SQAlchemyEnum(RegexType))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
