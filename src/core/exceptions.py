from fastapi import HTTPException, status


class ConflictException(HTTPException):
    def __init__(
        self,
        code: int = 1001,
        message: str = "Возник конфликт при создании данных.",
        status_code: int = status.HTTP_409_CONFLICT,
        exc: Exception | str | None = None,
    ):
        data = {
            "code": code,
            "message": message,
            "exc": exc,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )


class NotFoundException(HTTPException):
    def __init__(
        self,
        code: int = 1002,
        message: str = "Данные не найдены.",
        status_code: int = status.HTTP_404_NOT_FOUND,
    ):
        data = {
            "code": code,
            "message": message,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )


class BadRequestException(HTTPException):
    def __init__(
        self,
        code: int = 1003,
        message: str = "Некорректный запрос.",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        data = {
            "code": code,
            "message": message,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )


class ForbiddenException(HTTPException):
    def __init__(
        self,
        code: int = 1004,
        message: str = "Недостаточно привилегий для выполнения запроса.",
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


class InternalServerErrorException(HTTPException):
    def __init__(
        self,
        code: int = 1005,
        message: str = "Внутренняя ошибка сервера.",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        data = {
            "code": code,
            "message": message,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )
