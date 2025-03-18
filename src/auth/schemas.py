from datetime import datetime

from pydantic import BaseModel, Field

from src.base.schemas import EmailBaseSchema


# MARK: JWT
class JWTRefreshSchema(BaseModel):
    """Pydantic схема для обновления access и refresh токенов."""

    refresh_token: str = Field(description="refresh_token")


class JWTGetSchema(JWTRefreshSchema):
    """Pydantic схема для получения access и refresh токенов."""

    access_token: str = Field(description="access_token")
    expires_at: datetime = Field(description="Время действия `access_token`.")
    token_type: str = Field(default="Bearer", description="Тип `access_token`.")


# MARK: 2FA
class TwoFactorCodeCheckSchema(EmailBaseSchema):
    """Pydantic схема для получения кода 2FA."""

    code: str = Field(description="Код 2FA.")


class TwoFactorCodeSendSchema(EmailBaseSchema):
    """Pydantic схема для отправки кода 2FA."""

    pass


class Redis2FAValueSchema(BaseModel):
    """Pydantic схема для значения 2FA в Redis."""

    code_hash: str = Field(description="Хэш кода 2FA.")
    tries: int = Field(default=0, description="Количество попыток ввода кода 2FA.")
