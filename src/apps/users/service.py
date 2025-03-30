"""Модуль для сервиса пользователей."""

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.blockchain import schemas as blockchain_schemas
from src.apps.blockchain.services.transaction_service import (
    BlockchainTransactionService,
)
from src.apps.blockchain.services.tron_service import TronService
from src.apps.permissions.service import PermissionService
from src.apps.transactions.model import TransactionStatusEnum, TransactionTypeEnum
from src.apps.users.model import UserModel
from src.apps.users.repository import UserRepository
from src.apps.users.schemas import pay_schemas, user_schemas
from src.apps.users_permissions.service import UsersPermissionsService
from src.apps.wallets.service import WalletService
from src.core import constants, exceptions
from src.lib.base.service import BaseService
from src.lib.services.hash_service import HashService
from src.lib.services.random_service import RandomService


class UserService(
    BaseService[
        UserModel,
        user_schemas.UserCreateSchema,
        user_schemas.UserGetSchema,
        user_schemas.UsersPaginationSchema,
        user_schemas.UsersListGetSchema,
        user_schemas.UserUpdateSchema,
    ],
):
    """Сервис для работы с пользователями."""

    repository = UserRepository

    # MARK: Create
    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: user_schemas.UserCreateSchema,
    ) -> user_schemas.UserCreatedGetSchema:
        """
        Создать пользователя в БД.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            data (UserCreateSchema): Данные для создания пользователя.

        Returns:
            UserCreatedGetSchema: Добавленный пользователь.

        Raises:
            NotFoundException: Роль не найдена.
            ConflictException: Пользователь уже существует.
        """

        logger.info("Создание пользователя: {}", data)

        # Проверка существования разрешений
        if not await PermissionService.check_all_exist(
            session=session,
            ids=data.permissions_ids,
        ):
            raise exceptions.NotFoundException(
                message="Какие то разрешения не найдены.",
            )

        # Генерация и хэширование пароля
        password = RandomService.generate_str()
        hashed_password = HashService.generate(password)

        db_data = user_schemas.UserCreateRepositorySchema(
            email=data.email,
            hashed_password=hashed_password,
        )

        try:
            # Добавление пользователя в БД
            user = await cls.repository.create(
                session=session,
                obj_in=db_data,
            )

            # Добавление разрешений пользователю
            if data.permissions_ids:
                await UsersPermissionsService.add_permissions_to_user(
                    session=session,
                    user_id=user.id,
                    permission_ids=data.permissions_ids,
                )

            await session.commit()
            await session.refresh(user)

        except IntegrityError as ex:
            raise exceptions.ConflictException(exc=ex)

        return user_schemas.UserCreatedGetSchema(
            **user_schemas.UserGetSchema.model_validate(user).model_dump(),
            password=password,
        )

    # MARK: Update
    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        user_id: int,
        data: user_schemas.UserUpdateSchema,
    ) -> user_schemas.UserGetSchema:
        """
        Обновить данные пользователя.

        Args:
            session (AsyncSession): Сессия для работы с базой данных.
            user_id (int): ID пользователя.
            data (UserUpdateSchema): Данные для обновления пользователя.

        Returns:
            UserGetSchema: Обновленный пользователь.

        Raises:
            NotFoundException: Пользователь не найден.
            ConflictException: Пользователь с такими данными уже существует.
        """

        logger.info("Обновление пользователя с ID: {}", user_id)

        # Поиск пользователя в БД
        user = await cls.get_by_id(session, user_id)

        # Проверка существования разрешений
        if data.permissions_ids and not await PermissionService.check_all_exist(
            session=session,
            ids=data.permissions_ids,
        ):
            raise exceptions.NotFoundException(
                message="Какие то разрешения не найдены.",
            )

        hashed_password = None
        if data.password:
            hashed_password = HashService.generate(data.password)

        # Обновление пользователя в БД
        try:
            updated_user = await UserRepository.update(
                UserModel.id == user_id,
                session=session,
                obj_in=user_schemas.UserUpdateRepositorySchema(
                    email=data.email,
                    hashed_password=hashed_password,
                    is_active=data.is_active
                    if data.is_active is not None
                    else user.is_active,
                ),
            )

            # Обновление разрешений пользователя
            if data.permissions_ids:
                updated_user.permissions = await PermissionService.get_all_by_ids(
                    session=session,
                    ids=data.permissions_ids,
                )

            await session.commit()
            await session.refresh(updated_user)

        except IntegrityError as ex:
            raise exceptions.ConflictException(exc=ex)

        return user_schemas.UserGetSchema.model_validate(updated_user)

    @classmethod
    async def set_is_active(
        cls,
        session: AsyncSession,
        user: UserModel,
        is_active: bool,
    ) -> None:
        """
        Установить активность трейдера.

        Args:
            session: Сессия БД.
            user: Пользователь, который нужно установить в активный режим.
            is_active: Активный режим.

        Raises:
            ConflictException: Пользователь уже находится в этом режиме.
        """

        if user.is_active == is_active:
            raise exceptions.ConflictException(
                f"Трейдер уже в {'не' if is_active else ''} активном режиме."
            )

        user.is_active = is_active
        await session.commit()

    # MARK: Pay in
    @classmethod
    async def request_pay_in(
        cls, session: AsyncSession, user: UserModel, amount: int
    ) -> pay_schemas.ResponsePayInSchema:
        """
        Получить адрес кошелька на блокчейне с наименьшим балансом,
            куда нужно перевести средства.

        Создает сущность блокчейн транзакции в БД со статусом "ожидание".

        Args:
            session: Сессия БД.
            user: Пользователь, который запрашивает перевод средств.
            amount: Сумма перевода в TRX.

        Returns:
            Схема для ответа на запрос перевода средств.

        Raises:
            NotFoundException: Нет кошельков, куда можно перевести средства.
            ConflictException: Не удалось создать транзакцию или уже есть одна.
        """

        logger.info(
            "Запрос на перевод средств для пользователя с ID: {} суммой: {}",
            user.id,
            amount,
        )

        # Проверка на наличие транзакции в процессе обработки в БД
        try:
            await BlockchainTransactionService.get_pending_by_user_id(
                session=session,
                user_id=user.id,
                type=TransactionTypeEnum.PAY_IN,
            )

            raise exceptions.ConflictException(
                "У вас уже есть транзакция в процессе обработки."
            )

        except exceptions.NotFoundException:
            pass

        # Получение адресса кошелька с минимальным балансом с блокчейна
        wallet_address = await WalletService.get_wallet_address_with_min_or_max_balance(
            session=session, min_or_max="min", amount=amount
        )

        # Создание транзакции в БД
        await BlockchainTransactionService.create(
            session=session,
            data=blockchain_schemas.TransactionCreateSchema(
                user_id=user.id,
                to_address=wallet_address,
                amount=amount,
                type=TransactionTypeEnum.PAY_IN,
            ),
        )

        return pay_schemas.ResponsePayInSchema(wallet_address=wallet_address)

    @classmethod
    async def confirm_pay_in(
        cls, session: AsyncSession, user: UserModel, transaction_hash: str
    ) -> None:
        """
        Подтвердить перевод средств.

        Проверяет транзакцию по хэшу, изменяет статус транзакции в БД,
            и зачисляет средства на счет пользователя.

        Args:
            session: Сессия БД.
            user: Пользователь, который подтверждает перевод средств.
            transaction_hash: Хэш транзакции.

        Raises:
            NotFoundException: Транзакция не найдена.
            ConflictException: Не удалось обновить статус транзакции.
        """

        logger.info(
            "Подтверждение перевода средств от пользователя с ID: {} \
            транзакцией с хэшем: {}",
            user.id,
            transaction_hash,
        )

        # Получение транзакции в процессе обработки из БД
        transaction_db = await BlockchainTransactionService.get_pending_by_user_id(
            session=session,
            user_id=user.id,
            type=TransactionTypeEnum.PAY_IN,
        )

        # Получение транзакции по хэшу с блокчейна
        try:
            transaction = await TronService.get_transaction_by_hash(transaction_hash)

        except exceptions.NotFoundException as e:
            await BlockchainTransactionService.update_status_by_id(
                session=session,
                id=transaction_db.id,
                status=TransactionStatusEnum.FAILED,
            )
            raise e

        # Проверить данные транзакции с блокчейна с тразнакцией из БД
        if (
            transaction_db.amount != transaction["amount"]
            or transaction_db.to_address != transaction["to_address"]
            or transaction_db.type != TransactionTypeEnum.PAY_IN
        ):
            await BlockchainTransactionService.update_status_by_id(
                session=session,
                id=transaction_db.id,
                status=TransactionStatusEnum.FAILED,
            )
            raise exceptions.ConflictException("Транзакция не соответствует ожидаемой.")

        # Обновление статуса транзакции в БД на успешный
        await BlockchainTransactionService.update(
            session=session,
            id=transaction_db.id,
            data=blockchain_schemas.TransactionUpdateSchema(
                hash=transaction_hash,
                from_address=transaction["from_address"],
                status=TransactionStatusEnum.SUCCESS,
                created_at=transaction["created_at"],
            ),
        )

        # Зачисление средств на счет пользователя
        user.balance += transaction_db.amount
        await session.commit()

    # MARK: Pay out
    @classmethod
    async def request_pay_out(
        cls,
        session: AsyncSession,
        user: UserModel,
        data: pay_schemas.RequestPayOutSchema,
    ) -> pay_schemas.ResponsePayOutSchema:
        """
        Запросить вывод средств терминалом.

        Проверяет баланс пользователя,
            создает сущность блокчейн транзакции в БД со статусом "ожидание",
            которую нужно будет подтвердить суппортом.

        Args:
            session: Сессия БД.
            user: Пользователь, который запрашивает вывод средств.
            data: Схема для запроса вывода средств терминалом.

        Returns:
            Схема с идентификатором транзакции.

        Raises:
            NotFoundException: Нет кошельков, куда можно перевести средства.
            ConflictException: Не удалось создать транзакцию или уже есть одна.
        """

        logger.info(
            "Запрос на вывод средств терминалом от пользователя с ID: {} \
            суммой: {}",
            user.id,
            data.amount,
        )

        # Проверка баланса
        if (
            user.balance - user.amount_frozen
            < data.amount + data.amount * constants.COMMISSION
        ):
            raise exceptions.BadRequestException("Недостаточно средств для вывода.")

        # Проверка на наличие транзакции в процессе обработки в БД
        try:
            await BlockchainTransactionService.get_pending_by_user_id(
                session=session,
                user_id=user.id,
                type=TransactionTypeEnum.PAY_OUT,
            )

            raise exceptions.ConflictException(
                "У вас уже есть транзакция в процессе обработки."
            )

        except exceptions.NotFoundException:
            pass

        wallet_address = await WalletService.get_wallet_address_with_min_or_max_balance(
            session=session, min_or_max="max", amount=data.amount
        )

        transaction_db = await BlockchainTransactionService.create(
            session=session,
            data=blockchain_schemas.TransactionCreateSchema(
                user_id=user.id,
                to_address=data.to_address,
                from_address=wallet_address,
                amount=data.amount,
                type=TransactionTypeEnum.PAY_OUT,
            ),
        )

        return pay_schemas.ResponsePayOutSchema(transaction_id=transaction_db.id)
