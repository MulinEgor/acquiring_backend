"""Модуль для констант."""

from enum import StrEnum

from sqlalchemy import TextClause, text

from src.core.settings import settings

# MARK: Security
AUTH_HEADER_NAME: str = "Authorization"
ALGORITHM: str = "HS256"

CORS_HEADERS: list[str] = [
    "Content-Type",
    "Set-Cookie",
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Origin",
    AUTH_HEADER_NAME,
]
CORS_METHODS: list[str] = [
    "GET",
    "POST",
    "OPTIONS",
    "DELETE",
    "PATCH",
    "PUT",
]

# MARK: Database
DB_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
CURRENT_TIMESTAMP_UTC: TextClause = text("(CURRENT_TIMESTAMP AT TIME ZONE 'UTC')")
DEFAULT_QUERY_OFFSET: int = 0
DEFAULT_QUERY_LIMIT: int = 100


# MARK: Permissions
class PermissionEnum(StrEnum):
    """Перечисление разрешений."""

    # MARK: User
    GET_MY_USER = "получить своего пользователя"

    GET_USER = "получить пользователя"
    CREATE_USER = "создать пользователя"
    UPDATE_USER = "обновить пользователя"
    DELETE_USER = "удалить пользователя"

    REQUEST_PAY_IN = "запросить пополнение средств"
    CONFIRM_PAY_IN = "подтвердить пополнение средств"
    REQUEST_PAY_OUT = "запросить вывод средств"

    # MARK: Permission
    GET_PERMISSION = "получить разрешение"
    CREATE_PERMISSION = "создать разрешение"
    UPDATE_PERMISSION = "обновить разрешение"
    DELETE_PERMISSION = "удалить разрешение"

    # MARK: Wallet
    GET_WALLET = "получить кошелек"
    CREATE_WALLET = "создать кошелек"
    DELETE_WALLET = "удалить кошелек"

    # MARK: Blockchain Transaction
    GET_MY_BLOCKCHAIN_TRANSACTION = "получить свои транзакции блокчейна"

    GET_BLOCKCHAIN_TRANSACTION = "получить транзакцию блокчейна"
    CONFIRM_PAY_OUT_BLOCKCHAIN_TRANSACTION = (
        "подтвердить исходящую транзакцию блокчейна"
    )

    # MARK: Transactions
    GET_MY_TRANSACTION = "получить свои транзакции"

    GET_TRANSACTION = "получить транзакцию"
    CREATE_TRANSACTION = "создать транзакцию"
    UPDATE_TRANSACTION = "обновить транзакцию"
    DELETE_TRANSACTION = "удалить транзакцию"

    # MARK: Requisite
    CREATE_MY_REQUISITE = "создать свои реквизиты"
    GET_MY_REQUISITE = "получить свои реквизиты"
    UPDATE_MY_REQUISITE = "обновить свои реквизиты"
    DELETE_MY_REQUISITE = "удалить свои реквизиты"

    CREATE_REQUISITE = "создать реквизиты"
    GET_REQUISITE = "получить реквизиты"
    UPDATE_REQUISITE = "обновить реквизиты"
    DELETE_REQUISITE = "удалить реквизиты"

    # MARK: Trader
    CONFIRM_MERCHANT_PAY_IN_TRADER = (
        "подтвердить пополнение средств мерчантом как трейдер"
    )
    START_WORKING_TRADER = "начать работу как трейдер"
    STOP_WORKING_TRADER = "остановить работу как трейдер"

    # MARK: Merchant client
    REQUEST_PAY_IN_CLIENT = "запросить пополнение средств со стороны клиента"
    REQUEST_PAY_OUT_CLIENT = "запросить вывод средств со стороны клиента"

    # MARK: Support
    RESOLVE_DISPUTE = "решить диспут"

    # MARK: Disputes
    GET_MY_DISPUTE = "получить свои диспуты"
    UPDATE_MY_DISPUTE = "обновить свои диспуты"

    GET_DISPUTE = "получить диспут"
    CREATE_DISPUTE = "создать диспут"
    UPDATE_DISPUTE = "обновить диспут"
    DELETE_DISPUTE = "удалить диспут"

    # MARK: S3
    CREATE_FILE = "создать файл"
    GET_FILE = "получить файл"


# MARK: Redis
REDIS_EXPIRE_SECONDS: int = 60 * 15  # 15 минут

# MARK: SMTP
SMTP_SERVER: str = "smtp.gmail.com"
SMTP_PORT: int = 587

# MARK: 2FA
TWO_FACTOR_LOGIN_CONFIRM_SUBJECT: str = "Код подтверждения системы эквайринга"
TWO_FACTOR_LOGIN_CONFIRM_MESSAGE: str = "Здравствуйте! Ваш код подтверждения: {code}"
TWO_FACTOR_MAX_CODE_TRIES: int = 3

# MARK: Tron
TRON_JRPC_API_URL: str = "https://nile.trongrid.io/jsonrpc"
TRON_JRPC_VERSION: str = "2.0"
TRON_GET_TRANSACTION_BY_HASH_METHOD: str = "eth_getTransactionByHash"
TRON_GET_BALANCE_METHOD: str = "eth_getBalance"
TRON_GET_BLOCK_BY_HASH_METHOD: str = "eth_getBlockByHash"
TRON_CREATE_TRANSACTION_URL: str = "https://nile.trongrid.io/wallet/createtransaction"
TRON_BROADCAST_TRANSACTION_URL: str = (
    "https://nile.trongrid.io/wallet/broadcasttransaction"
)

# MARK: Transactions
PENDING_BLOCKCHAIN_TRANSACTION_TIMEOUT: int = 60 * 60 * 24  # 1 день
PENDING_TRANSACTION_TIMEOUT: int = 60 * 15  # 15 минут

# MARK: Disputes
PENDING_DISPUTE_TIMEOUT: int = 60 * 60 * 24  # 1 день

# MARK: Commissions
MERCHANT_COMMISSION: float = (
    0.1  # коммисия которая вычитается с баланса мерчанта, после проведения транзакции
)
TRADER_COMMISSION: float = (
    0.1  # коммисия которая идет на счет трейдера, после проведения транзакции
)
TRADER_DISPUTE_PENALTY: float = (
    0.2  # штраф который идет на счет мерчанта, если трейдер признает вину
)

# MARK: Celery
CELERY_BEAT_CHECK_BLOCKCHAIN_TRANSACTIONS_PERIOD: int = 60 * 10  # 10 минут
CELERY_BEAT_CHECK_TRANSACTIONS_PERIOD: int = 60 * 10  # 10 минут
CELERY_BEAT_CHECK_DISPUTES_PERIOD: int = 60 * 10  # 10 минут

# MARK: S3
S3_PUBLIC_BUCKET_POLICY: dict = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicRead",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{settings.S3_BUCKET_NAME}/*"],
        }
    ],
}
