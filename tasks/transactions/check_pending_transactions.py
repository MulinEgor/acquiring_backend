"""Модуль для проверки ожидающих транзакций на платформе."""

import asyncio
from datetime import datetime

from loguru import logger

from src.apps.notifications import schemas as notification_schemas
from src.apps.notifications.service import NotificationService
from src.apps.transactions.model import TransactionStatusEnum
from src.apps.transactions.repository import TransactionRepository
from src.apps.transactions.service import TransactionService
from src.core import constants
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

            for transaction_db in transactions_db:
                if transaction_db.expires_at < datetime.now():
                    transaction_db.status = TransactionStatusEnum.FAILED
                    await TransactionService.update_users_balances(
                        session=session,
                        transaction_db=transaction_db,
                    )

                    # Отправление уведомления
                    for user_id in [
                        transaction_db.trader_id,
                        transaction_db.merchant_id,
                    ]:
                        await NotificationService.create(
                            session=session,
                            data=notification_schemas.NotificationCreateSchema(
                                user_id=user_id,
                                message=constants.NOTIFICATION_MESSAGE_TRANSACTION_EXPIRED.format(
                                    transaction_id=transaction_db.id,
                                ),
                            ),
                        )

            await session.commit()

            logger.info(
                f"Обработано транзакций: {i * batch_size + len(transactions_db)}"
            )

        logger.info("Ожидающие транзакции платформы проверены.")
