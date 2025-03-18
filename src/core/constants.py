"""Модуль для констант."""

from enum import StrEnum

from sqlalchemy import TextClause, text

# MARK: Security
AUTH_HEADER_NAME: str = "X-Authorization"
ALGORITHM: str = "HS256"

CORS_HEADERS: list[str] = [
    "Content-Type",
    "Set-Cookie",
    "Access-Control-Allow-Headers",
    "Access-Control-Allow-Origin",
    "X-Authorization",
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
    GET_BLOCKCHAIN_TRANSACTION = "получить транзакцию блокчейна"

    # MARK: Trader
    REQUEST_PAY_IN_TRADER = "запросить пополнение средств как трейдер"
    CONFIRM_PAY_IN_TRADER = "подтвердить пополнение средств как трейдер"


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
TRON_API_URL: str = "https://api.shasta.trongrid.io/jsonrpc"
TRON_JRPC_VERSION: str = "2.0"
TRON_GET_TRANSACTION_BY_HASH_METHOD: str = "eth_getTransactionByHash"
TRON_GET_BALANCE_METHOD: str = "eth_getBalance"
TRON_GET_BLOCK_BY_HASH_METHOD: str = "eth_getBlockByHash"
