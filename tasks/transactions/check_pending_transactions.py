"""Модуль для проверки ожидающих транзакций на платформе."""

import asyncio
from datetime import datetime

from loguru import logger

from src.apps.transactions.model import TransactionStatusEnum, TransactionTypeEnum
from src.apps.transactions.repository import TransactionRepository
from src.apps.users.repository import UserRepository
from src.core.dependencies import get_session
from tasks.celery_worker import worker


@worker.task
def check_pending_transactions() -> None:
    """Задача для проверки ожидающих транзакций на платформе."""
    asyncio.run(_check_pending_transactions())


async def _check_pending_transactions() -> None:
    """
    Проверка ожидающих транзакций на платформе,
    а именно если транзакция не подтверждена и время ожидания истекло,
    то транзакция отменяется.

    Если транзакция типа "пополнение средств",
        то сумма размораживается на балансе трейдера.
    Если транзакция типа "списание средств",
        то сумма размораживается на балансе мерчанта.

    Проходимся по всем транзакциям с пагинацией.
    """

    async for session in get_session():
        logger.info("Получение ожидающих транзакций платформы...")

        i, batch_size = 0, 100
        while True:
            transactions_db = await TransactionRepository.get_all(
                session=session,
                limit=batch_size * (i + 1),
                offset=batch_size * i,
                status=TransactionStatusEnum.PENDING,
            )
            if not transactions_db:
                logger.info("Транзакций платформы в ожидании больше нет.")
                break
            i += 1

            for transaction in transactions_db:
                if transaction.expires_at < datetime.now():
                    transaction.status = TransactionStatusEnum.FAILED
                    if transaction.type == TransactionTypeEnum.PAY_IN:
                        trader_db = await UserRepository.get_one_or_none(
                            session=session,
                            id=transaction.trader_id,
                        )
                        trader_db.amount_frozen -= transaction.amount
                    else:
                        merchant_db = await UserRepository.get_one_or_none(
                            session=session,
                            id=transaction.merchant_id,
                        )
                        merchant_db.amount_frozen -= transaction.amount

            await session.commit()
            logger.info(
                f"Обработано транзакций: {i * batch_size + len(transactions_db)}"
            )

        logger.info("Ожидающие транзакции платформы проверены.")
