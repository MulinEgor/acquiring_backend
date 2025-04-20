from pydantic import BaseModel


# MARK: Pay in
class RequestPayInSchema(BaseModel):
    """Схема для получения адреса кошелька, куда нужно перевести средства."""

    amount: int


class ResponsePayInSchema(BaseModel):
    """Схема для ответа на запрос перевода средств."""

    wallet_address: str


class ConfirmPayInSchema(BaseModel):
    """Схема для подтверждения перевода средств на кошелек."""

    transaction_hash: str


# MARK: Pay out
class RequestPayOutSchema(BaseModel):
    """Схема для запроса вывода средств терминалом."""

    amount: int
    to_address: str


class ResponsePayOutSchema(BaseModel):
    """Схема для ответа на запрос вывода средств."""

    transaction_id: int
