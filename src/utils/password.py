"""Модуль для утилит, связанных с паролем."""

import random
import string


class PasswordGenerator:
    """Класс для генерации случайного пароля."""

    @classmethod
    def generate_password(cls) -> str:
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
