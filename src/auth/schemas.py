from datetime import datetime

from pydantic import BaseModel, Field


# MARK: JWT
class JWTRefreshSchema(BaseModel):
    """Pydantic схема для обновления access и refresh токенов."""

    refresh_token: str = Field(description="refresh_token")


class JWTGetSchema(JWTRefreshSchema):
    """Pydantic схема для получения access и refresh токенов."""

    access_token: str = Field(description="access_token")
    expires_at: datetime = Field(description="Время действия `access_token`.")
    token_type: str = Field(default="Bearer", description="Тип `access_token`.")
