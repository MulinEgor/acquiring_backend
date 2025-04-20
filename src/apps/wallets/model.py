from datetime import datetime

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class WalletModel(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    address: Mapped[str] = mapped_column(String(length=42), unique=True)
    private_key: Mapped[str] = mapped_column(String(length=66), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=datetime.now,
        onupdate=datetime.now,
    )
