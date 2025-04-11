from datetime import datetime

from pydantic import BaseModel, EmailStr


# MARK: JWT
class JWTRefreshSchema(BaseModel):
    """Pydantic схема для обновления access и refresh токенов."""

    refresh_token: str


class JWTGetSchema(JWTRefreshSchema):
    """Pydantic схема для получения access и refresh токенов."""

    access_token: str
    expires_at: datetime
    token_type: str = "Bearer"


# MARK: 2FA
class TwoFactorCodeCheckSchema(BaseModel):
    """Pydantic схема для получения кода 2FA."""

    email: EmailStr
    code: str


class TwoFactorCodeSendSchema(BaseModel):
    """Pydantic схема для отправки кода 2FA."""

    email: EmailStr


class Redis2FAValueSchema(BaseModel):
    """Pydantic схема для значения 2FA в Redis."""

    code_hash: str
    tries: int = 0
