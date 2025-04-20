import asyncio
from datetime import datetime

from loguru import logger

from src.apps.disputes.model import DisputeStatusEnum
from src.apps.disputes.repository import DisputeRepository
from src.apps.notifications import schemas as notification_schemas
from src.apps.notifications.service import NotificationService
from src.apps.transactions.repository import TransactionRepository
from src.apps.users.repository import UserRepository
from src.core import constants
from src.core.dependencies import get_session
from tasks.celery_worker import worker


@worker.task
def check_pending_disputes() -> None:
    asyncio.run(_check_pending_disputes())


async def _check_pending_disputes() -> None:
    """
    Проверка ожидающих диспутов на платформе,
    а именно если диспут не подтвержден и время ожидания истекло,
    то транзакция отменяется, и баланс трейдера возвращаются на место.

    Проходимся по всем диспутам с пагинацией.
    """
    async for session in get_session():
        logger.info("Получение ожидающих диспутов платформы...")

        i, batch_size = 0, 100
        while True:
            disputes_db = await DisputeRepository.get_all(
                session=session,
                limit=batch_size * (i + 1),
                offset=batch_size * i,
                status=DisputeStatusEnum.PENDING,
            )
            if not disputes_db:
                logger.info("Диспутов платформы в ожидании больше нет.")
                break
            i += 1

            for dispute_db in disputes_db:
                if dispute_db.expires_at < datetime.now():
                    dispute_db.status = DisputeStatusEnum.CLOSED
                    transaction_db = await TransactionRepository.get_one_or_none(
                        session=session,
                        id=dispute_db.transaction_id,
                    )
                    if transaction_db is None:
                        continue

                    trader_db = await UserRepository.get_one_or_none(
                        session=session,
                        id=transaction_db.trader_id,
                    )
                    if trader_db is None:
                        continue

                    # Разморозка средств трейдера
                    if (
                        dispute_db.winner_id is None
                        or dispute_db.winner_id == trader_db.id
                    ):
                        trader_db.amount_frozen -= transaction_db.amount
                    # Пополнение баланса мерчанта, списание средств с трейдера
                    else:
                        merchant_db = await UserRepository.get_one_or_none(
                            session=session,
                            id=transaction_db.merchant_id,
                        )
                        if merchant_db is None:
                            continue

                        merchant_db.balance += int(
                            transaction_db.amount
                            - transaction_db.amount
                            * constants.MERCHANT_TRANSACTION_COMMISSION
                        )
                        trader_db.amount_frozen -= transaction_db.amount
                        trader_db.balance -= int(
                            transaction_db.amount
                            + transaction_db.amount * constants.TRADER_DISPUTE_PENALTY
                        )

                    # Отправление уведомления
                    for user_id in [
                        transaction_db.merchant_id,
                        transaction_db.trader_id,
                    ]:
                        await NotificationService.create(
                            session=session,
                            data=notification_schemas.NotificationCreateSchema(
                                user_id=user_id,
                                message=constants.NOTIFICATION_MESSAGE_DISPUTE_EXPIRED.format(
                                    dispute_id=dispute_db.id,
                                ),
                            ),
                        )

            await session.commit()
            logger.info(f"Обработано диспутов: {i * batch_size + len(disputes_db)}")

        logger.info("Ожидающие диспуты платформы проверены.")
