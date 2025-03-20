"""Модуль для проверки ожидающих транзакций на блокчейне."""

import asyncio
from datetime import datetime

from loguru import logger

from src.apps.blockchain.models import StatusEnum
from src.apps.blockchain.repository import BlockchainTransactionRepository
from src.core.dependencies import get_session
from tasks.celery_worker import worker


@worker.task
def check_pending_transactions() -> None:
    """Задача для проверки ожидающих транзакций на блокчейне."""
    asyncio.run(_check_pending_transactions())


async def _check_pending_transactions() -> None:
    """
    Проверка ожидающих транзакций на блокчейне,
    а именно если транзакция не подтверждена и время ожидания истекло,
    то транзакция отменяется.

    Проходимся по всем транзакциям с пагинацией.
    """
    async for session in get_session():
        logger.info("Получение ожидающих транзакций блокчейна...")

        i, batch_size = 0, 100
        while True:
            transactions = await BlockchainTransactionRepository.get_all(
                session=session,
                limit=batch_size * (i + 1),
                offset=batch_size * i,
                status=StatusEnum.PENDING,
            )
            if not transactions:
                logger.info("Транзакций блокчейна в ожидании больше нет.")
                break
            i += 1

            for transaction in transactions:
                if transaction.expires_at < datetime.now():
                    transaction.status = StatusEnum.CANCELLED

            await session.commit()
            logger.info(f"Обработано транзакций: {i * batch_size + len(transactions)}")

        logger.info("Ожидающие транзакции блокчейна проверены.")
