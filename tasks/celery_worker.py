"""Модуль для работы с Celery."""

from celery import Celery

from src.core import constants
from src.core.settings import settings

worker = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
)


# Конфигурация Celery
worker.conf.imports = [
    # "tasks.transactions.check_pending_transactions",
    "tasks.blockchain.check_pending_transactions",
]


worker.conf.beat_schedule = {
    # "check_pending_transactions": {
    #     "task": "tasks.transactions.check_pending_transactions",
    #     "schedule": constants.CELERY_BEAT_CHECK_TRANSACTIONS_PERIOD,
    # },
    "check_pending_blockchain_transactions": {
        "task": (
            "tasks.blockchain.check_pending_transactions.check_pending_transactions"
        ),
        "schedule": constants.CELERY_BEAT_CHECK_BLOCKCHAIN_TRANSACTIONS_PERIOD,
    },
}
