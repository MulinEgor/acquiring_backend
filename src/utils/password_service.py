"""Модуль для утилит, связанных с паролем."""

import random
import string


class PasswordService:
    """Класс для генерации случайного пароля."""

    @staticmethod
    def generate() -> str:
        """
        Генерирует случайный пароль.

        Returns:
            str: Случайный пароль.
        """

        return "".join(
            random.choices(
                string.ascii_letters + string.digits + string.punctuation,
                k=random.randint(15, 30),
            )
        )
