from fastapi import HTTPException, status


class NotAuthorizedException(HTTPException):
    def __init__(
        self,
        code: int = 2001,
        message: str = "Вы не авторизованы.",
        status_code: int = status.HTTP_403_FORBIDDEN,
    ):
        data = {
            "code": code,
            "message": message,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )


# MARK: JWT
class TokenExpiredException(HTTPException):
    def __init__(
        self,
        code: int = 2002,
        message: str = "Время действия токена истекло.",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ):
        data = {
            "code": code,
            "message": message,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )


class InvalidTokenException(HTTPException):
    def __init__(
        self,
        code: int = 2003,
        message: str = "Невалидный токен.",
        status_code: int = status.HTTP_401_UNAUTHORIZED,
    ):
        data = {
            "code": code,
            "message": message,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )
