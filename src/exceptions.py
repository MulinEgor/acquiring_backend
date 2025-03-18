from sanic.exceptions import HTTPException


# MARK: JWT
class TokenExpired(HTTPException):
    """Возникает, если время действия токена истекло"""

    def __init__(
        self,
    ):
        super().__init__(
            status_code=401,
            detail="Время действия токена истекло.",
        )


class InvalidToken(HTTPException):
    """Возникает, если передан невалидный токен."""

    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Невалидный токен.",
        )
