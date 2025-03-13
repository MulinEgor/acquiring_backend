"""Модуль для утилит хэширования."""

import hashlib


# MARK: Hash
def get_hash(input: str) -> str:
    """
    Получить хэш строки.

    Args:
        input (str): Строка для хэширования.

    Returns:
        str: Хэш строки.
    """

    return hashlib.sha256(input.encode()).hexdigest()
