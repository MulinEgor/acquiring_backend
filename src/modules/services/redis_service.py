"""Модуль для сервиса Redis."""

from redis import asyncio as aioredis

from src.core import constants
from src.core.settings import settings


class RedisService:
    """Класс для сервиса Redis."""

    _redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        decode_responses=True,
    )

    @classmethod
    async def set(
        cls, key: str, value: str, expire: int = constants.REDIS_EXPIRE_SECONDS
    ) -> None:
        """
        Метод для установки значения в Redis с автоматическим удалением через 15 минут.

        Args:
            key (str): Ключ для установки значения.
            value (str): Значение для установки.
            expire (int): Время жизни ключа в секундах.
        """
        await cls._redis.set(key, value, ex=expire)

    @classmethod
    async def get(cls, key: str) -> str | None:
        """
        Метод для получения значения из Redis.

        Args:
            key (str): Ключ для получения значения.

        Returns:
            str | None: Значение из Redis.
        """
        return await cls._redis.get(key)

    @classmethod
    async def delete(cls, key: str) -> None:
        """
        Метод для удаления значения из Redis.

        Args:
            key (str): Ключ для удаления значения.
        """
        await cls._redis.delete(key)
