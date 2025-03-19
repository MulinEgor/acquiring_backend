"""Модуль для сервиса для работы с Tron."""

import asyncio
import random
from datetime import datetime

import aiohttp
import orjson
from loguru import logger

from src.core import constants, exceptions


class TronService:
    """Сервис для работы с Tron."""

    @classmethod
    async def _get_block_timestamp(cls, hash: str) -> int:
        """
        Получить timestamp блока.

        Args:
            hash: Хэш блока.

        Returns:
            Timestamp блока.
        """

        logger.info("Получение timestamp блока по хэшу: {}", hash)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                constants.TRON_API_URL,
                json={
                    "jsonrpc": constants.TRON_JRPC_VERSION,
                    "method": constants.TRON_GET_BLOCK_BY_HASH_METHOD,
                    "params": [hash, False],
                    "id": random.randint(1, 1000000),
                },
            ) as response:
                if response.status != 200:
                    logger.warning(
                        "Ошибка при попытке получения блока по хэшу: {} \
                        status: {}, text: {}.",
                        response.status,
                        await response.text(),
                    )
                    raise exceptions.InternalServerErrorException(
                        f"Ошибка при попытке получения блока с TronScan: \
                        status: {response.status}, text: {await response.text()}."
                    )

                block_data: dict = orjson.loads(await response.text())

        if block_data.get("result") is None:
            logger.warning("Блок с хэшем: {} не найден", hash)
            raise exceptions.NotFoundException("Блок не найден.")

        logger.success("Блок с хэшем: {} найден", hash)

        return int(block_data["result"]["timestamp"], 16)

    @staticmethod
    async def does_wallet_exist(address: str) -> bool:
        """
        Проверить, существует ли кошелек.

        Args:
            address: Адрес кошелька.

        Returns:
            True, если кошелек существует, False - в противном случае.
        """

        logger.info("Проверка существования кошелька: {}", address)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                constants.TRON_API_URL,
                json={
                    "jsonrpc": constants.TRON_JRPC_VERSION,
                    "method": constants.TRON_GET_BALANCE_METHOD,
                    "params": [address, "latest"],
                    "id": random.randint(1, 1000000),
                },
            ) as response:
                if response.status != 200:
                    logger.warning(
                        "Ошибка при попытке получения кошелька: {} \
                        status: {}, text: {}.",
                        address,
                        response.status,
                        await response.text(),
                    )
                    raise exceptions.InternalServerErrorException(
                        f"Ошибка при попытке получения кошелька с Tron API: \
                        status: {response.status}, text: {await response.text()}."
                    )

                data_json: dict = orjson.loads(await response.text())

        if data_json.get("result") is None:
            logger.warning("Кошелек: {} не существует", address)
            return False

        logger.success("Кошелек: {} существует", address)

        return True

    @staticmethod
    async def get_wallets_balances(addresses: list[str]) -> dict[str, int]:
        """
        Получить балансы кошельков.
        Обращается к API TronScan и получает балансы кошельков.

        Args:
            addresses: Список адресов кошельков.

        Returns:
            Словарь с адресами кошельков и их балансами.
        """

        logger.info("Получение балансов кошельков: {}", addresses)

        balances: dict[str, int] = {}

        async with aiohttp.ClientSession() as session:
            tasks = [
                session.post(
                    constants.TRON_API_URL,
                    json={
                        "jsonrpc": constants.TRON_JRPC_VERSION,
                        "method": constants.TRON_GET_BALANCE_METHOD,
                        "params": [address, "latest"],
                        "id": random.randint(1, 1000000),
                    },
                )
                for address in addresses
            ]
            for i, response in enumerate(await asyncio.gather(*tasks)):
                if response.status == 200:
                    logger.info("Получение баланса кошелька: {}", addresses[i])

                    data_json: dict = orjson.loads(await response.text())
                    if data_json.get("result") is not None:
                        balances[addresses[i]] = int(
                            data_json["result"], 16
                        )  # Конвертация в 10-ричную систему

        logger.success("Балансы кошельков получены: {}", balances)

        return balances

    @classmethod
    async def get_transaction_by_hash(cls, hash: str) -> dict:
        """
        Получить транзакцию по хэшу.

        Args:
            hash: Хэш транзакции.

        Returns:
            Словарь с данными транзакции:
                (hash, from_address, to_address, amount, created_at)

        Raises:
            InternalServerErrorException:
                Ошибка при попытке получения транзакции с TronScan.
            NotFoundException: Транзакция не найдена.
        """

        logger.info("Получение транзакции по хэшу: {}", hash)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                constants.TRON_API_URL,
                json={
                    "jsonrpc": constants.TRON_JRPC_VERSION,
                    "method": constants.TRON_GET_TRANSACTION_BY_HASH_METHOD,
                    "params": [hash],
                    "id": random.randint(1, 1000000),
                },
            ) as response:
                if response.status != 200:
                    logger.warning(
                        "Ошибка при попытке получения транзакции: {} \
                        status: {}, text: {}.",
                        hash,
                        response.status,
                        await response.text(),
                    )
                    raise exceptions.InternalServerErrorException(
                        f"Ошибка при попытке получения транзакции с TronScan: \
                        status: {response.status}, text: {await response.text()}."
                    )

                data_json: dict = orjson.loads(await response.text())

        if data_json.get("result") is None:
            logger.warning("Транзакция с хэшем: {} не найдена", hash)
            raise exceptions.NotFoundException("Транзакция не найдена.")

        logger.success("Транзакция с хэшем: {} найдена", hash)

        return {
            "hash": data_json["result"]["hash"],
            "from_address": data_json["result"]["from"],
            "to_address": data_json["result"]["to"],
            "amount": int(data_json["result"]["value"], 16),
            "created_at": datetime.fromtimestamp(
                await cls._get_block_timestamp(data_json["result"]["blockHash"])
            ),
        }
