"""Модуль для сервиса для работы с TronScan."""

import aiohttp
import orjson

from src import exceptions


class TronScanService:
    """Сервис для работы с TronScan."""

    @staticmethod
    async def does_wallet_exist(address: str) -> bool:
        """
        Проверить, существует ли кошелек.

        Args:
            address: Адрес кошелька.

        Returns:
            True, если кошелек существует, False - в противном случае.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://apilist.tronscanapi.com/api/contract?contract={address}"
            ) as response:
                if response.status != 200:
                    raise exceptions.InternalServerErrorException(
                        f"Ошибка при попытке получения кошелька с TronScan: \
                        status: {response.status}, text: {await response.text()}."
                    )

                data_json = orjson.loads(await response.text())

        return len(data_json["data"][0]["address"]) > 0
