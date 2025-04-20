import asyncio
import hashlib
import random
from datetime import datetime

import aiohttp
import orjson
from tronpy.keys import PrivateKey

from src.core import constants, exceptions
from src.core.settings import settings


class TronService:
    """Сервис для работы с Tron."""

    # MARK: Utils
    @classmethod
    async def _get_block_timestamp(cls, hash: str) -> int:
        """
        Получить timestamp блока.

        Args:
            hash: Хэш блока.

        Returns:
            Timestamp блока.
        """

        async with aiohttp.ClientSession() as session:
            async with session.post(
                constants.TRON_JRPC_API_URL,
                json={
                    "jsonrpc": constants.TRON_JRPC_VERSION,
                    "method": constants.TRON_GET_BLOCK_BY_HASH_METHOD,
                    "params": [hash, False],
                    "id": random.randint(1, 1000000),
                },
                headers={
                    "TRON-PRO-API-KEY": settings.TRON_API_KEY,
                },
            ) as response:
                if response.status != 200:
                    raise exceptions.InternalServerErrorException(
                        f"Ошибка при попытке получения блока с TronScan: \
                        status: {response.status}, text: {await response.text()}."
                    )

                block_data: dict = orjson.loads(await response.text())

        if block_data.get("result") is None:
            raise exceptions.NotFoundException("Блок не найден.")

        return int(block_data["result"]["timestamp"], 16)

    # MARK: Check
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
            async with session.post(
                constants.TRON_JRPC_API_URL,
                json={
                    "jsonrpc": constants.TRON_JRPC_VERSION,
                    "method": constants.TRON_GET_BALANCE_METHOD,
                    "params": [address, "latest"],
                    "id": random.randint(1, 1000000),
                },
                headers={
                    "TRON-PRO-API-KEY": settings.TRON_API_KEY,
                },
            ) as response:
                if response.status != 200:
                    raise exceptions.InternalServerErrorException(
                        f"Ошибка при попытке получения кошелька с Tron API: \
                        status: {response.status}, text: {await response.text()}."
                    )

                data_json: dict = orjson.loads(await response.text())

        if data_json.get("result") is None:
            return False

        return True

    # MARK: Get
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

        balances: dict[str, int] = {}

        async with aiohttp.ClientSession() as session:
            tasks = [
                session.post(
                    constants.TRON_JRPC_API_URL,
                    json={
                        "jsonrpc": constants.TRON_JRPC_VERSION,
                        "method": constants.TRON_GET_BALANCE_METHOD,
                        "params": [address, "latest"],
                        "id": random.randint(1, 1000000),
                    },
                    headers={
                        "TRON-PRO-API-KEY": settings.TRON_API_KEY,
                    },
                )
                for address in addresses
            ]
            for i, response in enumerate(await asyncio.gather(*tasks)):
                if response.status == 200:
                    data_json: dict = orjson.loads(await response.text())
                    if data_json.get("result") is not None:
                        balances[addresses[i]] = int(
                            data_json["result"], 16
                        )  # Конвертация в 10-ричную систему

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

        async with aiohttp.ClientSession() as session:
            async with session.post(
                constants.TRON_JRPC_API_URL,
                json={
                    "jsonrpc": constants.TRON_JRPC_VERSION,
                    "method": constants.TRON_GET_TRANSACTION_BY_HASH_METHOD,
                    "params": [hash],
                    "id": random.randint(1, 1000000),
                },
                headers={
                    "TRON-PRO-API-KEY": settings.TRON_API_KEY,
                },
            ) as response:
                if response.status != 200:
                    raise exceptions.InternalServerErrorException(
                        f"Ошибка при попытке получения транзакции с TronScan: \
                        status: {response.status}, text: {await response.text()}."
                    )

                data_json: dict = orjson.loads(await response.text())

        if data_json.get("result") is None:
            raise exceptions.NotFoundException("Транзакция не найдена.")

        return {
            "hash": data_json["result"]["hash"],
            "from_address": data_json["result"]["from"],
            "to_address": data_json["result"]["to"],
            "amount": int(data_json["result"]["value"], 16),
            "created_at": datetime.fromtimestamp(
                await cls._get_block_timestamp(data_json["result"]["blockHash"])
            ),
        }

    # MARK: Confirm
    @staticmethod
    async def _create_transaction(
        from_address: str,
        to_address: str,
        amount: int,
    ) -> dict:
        """
        Создание транзакции через TRON API.

        Args:
            from_address: Адрес отправителя.
            to_address: Адрес получателя.
            amount: Сумма транзакции.

        Returns:
            Словарь с данными транзакции.
        """

        async with aiohttp.ClientSession() as session:
            async with session.post(
                constants.TRON_CREATE_TRANSACTION_URL,
                json={
                    "owner_address": from_address,
                    "to_address": to_address,
                    "amount": amount,
                    "visible": True,
                },
                headers={
                    "TRON-PRO-API-KEY": settings.TRON_API_KEY,
                },
            ) as response:
                if response.status != 200:
                    raise exceptions.InternalServerErrorException(
                        f"Ошибка при попытке создать транзакцию с Tron API: \
                        статус: {response.status}, текст: {await response.text()}."
                    )
                data = orjson.loads(await response.text())

                if data.get("Error"):
                    raise exceptions.InternalServerErrorException(
                        f"Ошибка при попытке создать транзакцию с Tron API: \
                        текст: {data.get('Error')}."
                    )

                return data

    @staticmethod
    async def _sign_transaction(transaction: dict, private_key: str) -> dict:
        """
        Подписание транзакции используя tronpy с приватным ключом.

        Args:
            transaction: Транзакция.
            private_key: Приватный ключ.

        Returns:
            Транзакция с подписью.
        """

        private_key = PrivateKey(bytes.fromhex(private_key))

        msg_hash = hashlib.sha256(bytes.fromhex(transaction["raw_data_hex"])).digest()
        signature = private_key.sign_msg_hash(msg_hash)
        transaction["signature"] = [signature.hex()]

        return transaction

    @staticmethod
    async def _broadcast_transaction(signed_transaction: dict) -> None:
        """
        Отправка подписанной транзакции в сеть.

        Args:
            signed_transaction: Подписанная транзакция.
        """

        async with aiohttp.ClientSession() as session:
            async with session.post(
                constants.TRON_BROADCAST_TRANSACTION_URL,
                json=signed_transaction,
                headers={
                    "TRON-PRO-API-KEY": settings.TRON_API_KEY,
                },
            ) as response:
                if response.status != 200:
                    raise exceptions.InternalServerErrorException(
                        f"Ошибка при попытке отправить транзакцию: \
                        status: {response.status}, text: {await response.text()}."
                    )

    @classmethod
    async def create_and_sign_transaction(
        cls,
        from_address: str,
        to_address: str,
        amount: int,
        private_key: str,
    ) -> str:
        """
        Отправить и подписать транзакцию на блокчейне.

        Args:
            from_address: Адрес отправителя.
            to_address: Адрес получателя.
            amount: Сумма транзакции.
            private_key: Приватный ключ.

        Returns:
            Хэш транзакции.

        Raises:
            InternalServerErrorException: Ошибка при попытке отправить транзакцию.
        """

        transaction = await cls._create_transaction(
            from_address,
            to_address,
            amount,
        )
        signed_transaction = await cls._sign_transaction(transaction, private_key)
        await cls._broadcast_transaction(signed_transaction)

        return transaction["txID"]
