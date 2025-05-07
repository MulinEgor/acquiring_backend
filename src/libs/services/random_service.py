import random
import string


class RandomService:
    """Класс для генерации случайных значений."""

    @staticmethod
    def generate_str() -> str:
        """
        Генерирует случайную строку из букв, цифр и символов.

        Returns:
            str: Случайная строка.
        """

        return "".join(
            random.choices(
                string.ascii_letters + string.digits,
                k=random.randint(15, 30),
            )
        )
