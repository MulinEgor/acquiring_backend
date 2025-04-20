from datetime import datetime, timedelta

from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.apps.transactions.model import TransactionStatusEnum, TransactionTypeEnum
from src.core import constants
from src.core.database import Base


class BlockchainTransactionModel(Base):
    """Модель транзакции на блокчейне."""

    __tablename__ = "blockchain_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column()
    type: Mapped[TransactionTypeEnum] = mapped_column(
        SQLAlchemyEnum(TransactionTypeEnum)
    )
    from_address: Mapped[str] = mapped_column(String(42), nullable=True)
    to_address: Mapped[str] = mapped_column(String(42))
    status: Mapped[TransactionStatusEnum] = mapped_column(
        SQLAlchemyEnum(TransactionStatusEnum), default=TransactionStatusEnum.PENDING
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
