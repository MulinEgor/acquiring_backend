"""Модуль для утилит хэширования."""

import hashlib


class HashService:
    """Класс для утилит хэширования."""

    @staticmethod
    def generate(input: str) -> str:
        """
        Получить хэш строки.

        Args:
            input (str): Строка для хэширования.

        Returns:
            str: Хэш строки.
        """

        return hashlib.sha256(input.encode()).hexdigest()
