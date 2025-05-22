from fastapi import HTTPException, status


class GetTronBlockException(HTTPException):
    def __init__(
        self,
        error_status_code: int,
        error_text: str,
        code: int = 4001,
        message: str = "Ошибка при попытке получения блока с Tron.",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        data = {
            "code": code,
            "message": message,
            "error_status_code": error_status_code,
            "error_text": error_text,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )


class GetTronWalletException(HTTPException):
    def __init__(
        self,
        error_status_code: int,
        error_text: str,
        code: int = 4002,
        message: str = "Ошибка при попытке получения кошелька с Tron.",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        data = {
            "code": code,
            "message": message,
            "error_status_code": error_status_code,
            "error_text": error_text,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )


class GetTronTransactionException(HTTPException):
    def __init__(
        self,
        error_status_code: int,
        error_text: str,
        code: int = 4003,
        message: str = "Ошибка при попытке получения транзакции с Tron.",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        data = {
            "code": code,
            "message": message,
            "error_status_code": error_status_code,
            "error_text": error_text,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )


class CreateTronTransactionException(HTTPException):
    def __init__(
        self,
        error_status_code: int,
        error_text: str,
        code: int = 4004,
        message: str = "Ошибка при попытке создать транзакцию с Tron.",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        data = {
            "code": code,
            "message": message,
            "error_status_code": error_status_code,
            "error_text": error_text,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )


class BroadcastTronTransactionException(HTTPException):
    def __init__(
        self,
        error_status_code: int,
        error_text: str,
        code: int = 4005,
        message: str = "Ошибка при попытке отправить транзакцию.",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        data = {
            "code": code,
            "message": message,
            "error_status_code": error_status_code,
            "error_text": error_text,
        }

        super().__init__(
            status_code=status_code,
            detail=data,
        )
