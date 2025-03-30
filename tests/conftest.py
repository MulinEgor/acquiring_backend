"""Основной модуль `conftest` для всех тестов."""

import asyncio
import sys
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from faker import Faker
from loguru import logger
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.apps.auth import schemas as auth_schemas
from src.apps.auth.services.jwt_service import JWTService
from src.apps.blockchain.model import BlockchainTransactionModel
from src.apps.disputes import schemas as dispute_schemas
from src.apps.disputes.model import DisputeModel
from src.apps.disputes.repository import DisputeRepository
from src.apps.merchants import schemas as merchant_schemas
from src.apps.permissions import schemas as permission_schemas
from src.apps.permissions.model import PermissionModel
from src.apps.permissions.repository import PermissionRepository
from src.apps.requisites import schemas as requisite_schemas
from src.apps.requisites.model import RequisiteModel
from src.apps.requisites.repository import RequisiteRepository
from src.apps.transactions import schemas as transaction_schemas
from src.apps.transactions.model import (
    TransactionModel,
    TransactionPaymentMethodEnum,
    TransactionStatusEnum,
    TransactionTypeEnum,
)
from src.apps.users.model import UserModel
from src.apps.users.schemas import user_schemas
from src.apps.users_permissions.repository import UsersPermissionsRepository
from src.apps.wallets import schemas as wallet_schemas
from src.apps.wallets.model import WalletModel
from src.core import constants
from src.core.settings import settings
from src.lib.services.hash_service import HashService

faker = Faker()


# MARK: DBSession
@pytest_asyncio.fixture(scope="module")
async def engine(request) -> AsyncGenerator[AsyncEngine, None]:
    """
    Создает экземпляр `AsyncEngine` с URL-адресом базы данных,
    соответствующим процессу pytest.

    Область действия `module` задается, поскольку каждый модуль c тестами
    выполняется в отдельном процессе pytest, чтобы гарантировать, что
    он подключается к соответствующей базе данных.
    """

    engine = create_async_engine(
        url=settings.DATABASE_URL,
        poolclass=NullPool,
    )

    yield engine


@pytest.fixture(scope="function")
async def session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Создать соединение с Postgres, начать транзакцию,
    а затем привязать это соединение к сессии с вложенной транзакцией.

    Вложенная транзакция обеспечивает изоляцию внутри тестов, позволяя
    фиксировать изменения во внутренней транзакции так, чтобы они были
    видны только для тестов, где она используется, но не фиксировать их
    в БД полностью, поскольку коммит внешней транзакции
    никогда не будет выполнен.

    Параметр `scope="function"` обеспечивает запуск этой фикстуры перед запуском каждого
    теста. Так что после запуска каждого теста, данные в БД откатываются.
    Каждый тест работает изолированно от других.

    Используется движок, соответствующий процессу `pytest`.
    """

    AsyncSession = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with engine.connect() as conn:
        tsx = await conn.begin()
        async with AsyncSession(bind=conn) as session:
            nested_tsx = await conn.begin_nested()

            yield session

            if nested_tsx.is_active:
                await nested_tsx.rollback()
            await tsx.rollback()


@pytest.fixture(scope="session", autouse=True)
def disable_logger():
    """Отключить логирование для тестов."""
    logger.configure(handlers=[{"sink": sys.stderr, "level": "CRITICAL"}])


@pytest.fixture()
def task_session(
    session: AsyncSession,
    mocker,
) -> AsyncSession:
    """Мокирование сессии для выполнения задач Celery."""

    async def mock_get_session():
        yield session

    mocker.patch("tasks.db_session.get_session", return_value=mock_get_session())
    return session


# MARK: Loop
@pytest.fixture(scope="session")
def event_loop(request):
    """
    Фикстура для создания и закрытия event loop.
    """

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# MARK: Output
@pytest.fixture(autouse=True, scope="session")
def output_to_stdout():
    """
    Перенаправить `stdout` в `stderr`,
    для вывода логов при отладки в `pytest-xdist`.
    """

    sys.stdout = sys.stderr


# MARK: Redis
@pytest_asyncio.fixture(autouse=True)
async def mock_redis(mocker):
    """Мокирование Redis."""

    mocker.patch("src.lib.services.redis_service.RedisService.get", return_value=None)
    mocker.patch("src.lib.services.redis_service.RedisService.set", return_value=None)
    mocker.patch(
        "src.lib.services.redis_service.RedisService.delete", return_value=None
    )


# MARK: Permissions
@pytest_asyncio.fixture
async def permission_db(session: AsyncSession) -> PermissionModel:
    """Добавить разрешение в БД."""

    permission = PermissionModel(
        name=faker.word(),
    )
    session.add(permission)
    await session.commit()

    return permission


@pytest.fixture
def permission_create_data() -> permission_schemas.PermissionCreateSchema:
    """Подготовленные данные для создания разрешения в БД."""

    return permission_schemas.PermissionCreateSchema(
        name=faker.word(),
    )


# MARK: Users
@pytest_asyncio.fixture
async def user_db(session: AsyncSession) -> UserModel:
    """Добавить пользователя в БД."""

    user_db = UserModel(
        email=faker.email(),
        hashed_password=HashService.generate(faker.password()),
    )
    session.add(user_db)
    await session.commit()

    user_permissions = [constants.PermissionEnum.GET_MY_USER]
    for permission in user_permissions:
        permission_db = await PermissionRepository.get_one_or_none(
            session=session,
            name=permission.value,
        )
        await UsersPermissionsRepository.create(
            session=session,
            obj_in={
                "user_id": user_db.id,
                "permission_id": permission_db.id,
            },
        )

    await session.commit()

    return user_db


@pytest_asyncio.fixture
async def user_db_2fa(session: AsyncSession, user_db: UserModel) -> UserModel:
    """Добавить пользователя в БД с 2FA."""

    user_db.is_2fa_enabled = True
    await session.commit()

    return user_db


@pytest_asyncio.fixture
async def user_admin_db(
    session: AsyncSession,
) -> UserModel:
    """Добавить пользователя-администратора в БД."""

    user_admin_db = UserModel(
        email=faker.email(),
        hashed_password=HashService.generate(faker.password()),
    )
    session.add(user_admin_db)

    await session.commit()

    permissions_db = await PermissionRepository.get_all(session)
    await UsersPermissionsRepository.create_bulk(
        session=session,
        data=[
            {
                "user_id": user_admin_db.id,
                "permission_id": permission.id,
            }
            for permission in permissions_db
        ],
    )

    await session.commit()

    return user_admin_db


@pytest_asyncio.fixture
async def user_trader_db_with_sbp(
    session: AsyncSession,
) -> UserModel:
    """Добавить пользователя-трейдера в БД."""

    user_trader_db_with_sbp = UserModel(
        email=faker.email(),
        hashed_password=HashService.generate(faker.password()),
        is_active=True,
    )
    session.add(user_trader_db_with_sbp)

    await session.commit()

    trader_permissions = [
        constants.PermissionEnum.REQUEST_PAY_IN,
        constants.PermissionEnum.CONFIRM_PAY_IN,
        constants.PermissionEnum.REQUEST_PAY_OUT,
        constants.PermissionEnum.GET_MY_BLOCKCHAIN_TRANSACTION,
        constants.PermissionEnum.CREATE_MY_REQUISITE,
        constants.PermissionEnum.GET_MY_REQUISITE,
        constants.PermissionEnum.UPDATE_MY_REQUISITE,
        constants.PermissionEnum.DELETE_MY_REQUISITE,
        constants.PermissionEnum.GET_MY_TRANSACTION,
        constants.PermissionEnum.CONFIRM_MERCHANT_PAY_IN_TRADER,
        constants.PermissionEnum.START_WORKING_TRADER,
        constants.PermissionEnum.STOP_WORKING_TRADER,
        constants.PermissionEnum.UPDATE_MY_DISPUTE,
        constants.PermissionEnum.GET_MY_DISPUTE,
        constants.PermissionEnum.CONFIRM_MERCHANT_PAY_OUT_TRADER,
    ]
    permissions_db = await PermissionRepository.get_all(session)
    await UsersPermissionsRepository.create_bulk(
        session=session,
        data=[
            {
                "user_id": user_trader_db_with_sbp.id,
                "permission_id": permission.id,
            }
            for permission in permissions_db
            if permission.name in trader_permissions
        ],
    )

    await session.commit()

    requisite_db = RequisiteModel(
        user_id=user_trader_db_with_sbp.id,
        full_name=faker.word(),
        phone_number=faker.phone_number(),
        bank_name=faker.word(),
    )
    session.add(requisite_db)
    await session.commit()

    user_trader_db_with_sbp.balance = 1000000
    await session.commit()

    return user_trader_db_with_sbp


@pytest_asyncio.fixture
async def user_trader_db_with_card(
    session: AsyncSession,
    user_trader_db_with_sbp: UserModel,
) -> UserModel:
    """Добавить пользователя-трейдера в БД."""

    old_requisite_db = await RequisiteRepository.get_one_or_none(
        session=session,
        user_id=user_trader_db_with_sbp.id,
    )
    if old_requisite_db:
        await session.delete(old_requisite_db)

    requisite_db = RequisiteModel(
        user_id=user_trader_db_with_sbp.id,
        full_name=faker.word(),
        card_number=faker.word(),
    )
    session.add(requisite_db)
    await session.commit()

    return user_trader_db_with_sbp


@pytest_asyncio.fixture
async def user_merchant_db(
    session: AsyncSession,
) -> UserModel:
    """Добавить пользователя-мерчанта в БД."""

    user_merchant_db = UserModel(
        email=faker.email(),
        hashed_password=HashService.generate(faker.password()),
    )
    session.add(user_merchant_db)

    await session.commit()

    merchant_permissions = [
        constants.PermissionEnum.GET_MY_TRANSACTION,
        constants.PermissionEnum.REQUEST_PAY_IN_CLIENT,
        constants.PermissionEnum.CREATE_DISPUTE,
        constants.PermissionEnum.GET_MY_DISPUTE,
        constants.PermissionEnum.REQUEST_PAY_OUT_CLIENT,
    ]
    permissions_db = await PermissionRepository.get_all(session)
    await UsersPermissionsRepository.create_bulk(
        session=session,
        data=[
            {
                "user_id": user_merchant_db.id,
                "permission_id": permission.id,
            }
            for permission in permissions_db
            if permission.name in merchant_permissions
        ],
    )

    await session.commit()

    return user_merchant_db


@pytest.fixture
def user_create_data(
    permission_db: PermissionModel,
) -> user_schemas.UserCreateSchema:
    """
    Подготовленные данные для создания
    пользователя в БД администратором.
    """

    return user_schemas.UserCreateSchema(
        email=faker.email(),
        permissions_ids=[permission_db.id],
    )


@pytest.fixture
def user_update_data() -> user_schemas.UserUpdateSchema:
    """
    Подготовленные данные для обновления
    пользователя в БД администратором.
    """

    return user_schemas.UserUpdateSchema(
        email=faker.email(),
        password=faker.password(),
    )


# MARK: JWT tokens
@pytest_asyncio.fixture
async def user_jwt_tokens(user_db: UserModel) -> auth_schemas.JWTGetSchema:
    """Создать JWT токены  для тестового пользователя."""

    return await JWTService.create_tokens(user_id=user_db.id)


@pytest_asyncio.fixture
async def admin_jwt_tokens(user_admin_db: UserModel) -> auth_schemas.JWTGetSchema:
    """Создать JWT токены  для тестового пользователя-администратора."""

    return await JWTService.create_tokens(user_id=user_admin_db.id)


@pytest_asyncio.fixture
async def trader_jwt_tokens(
    user_trader_db_with_sbp: UserModel,
) -> auth_schemas.JWTGetSchema:
    """Создать JWT токены  для тестового пользователя-трейдера."""

    return await JWTService.create_tokens(user_id=user_trader_db_with_sbp.id)


@pytest_asyncio.fixture
async def merchant_jwt_tokens(user_merchant_db: UserModel) -> auth_schemas.JWTGetSchema:
    """Создать JWT токены  для тестового пользователя-мерчанта."""

    return await JWTService.create_tokens(user_id=user_merchant_db.id)


# MARK: Wallets
@pytest_asyncio.fixture
async def wallet_db(session: AsyncSession) -> WalletModel:
    """Добавить кошелек в БД."""

    wallet = WalletModel(
        address="*" * 42,  # тестовая строка с нужной длинойs
        private_key="*" * 66,  # тестовая строка с нужной длиной
    )
    session.add(wallet)
    await session.commit()

    return wallet


@pytest.fixture
def wallet_create_data() -> wallet_schemas.WalletCreateSchema:
    """Подготовленные данные для создания кошелька в БД."""

    return wallet_schemas.WalletCreateSchema(
        address="*" * 42,  # тестовая строка с нужной длинойs
        private_key="*" * 66,  # тестовая строка с нужной длиной
    )


# MARK: Blockchain transactions
@pytest_asyncio.fixture
async def blockchain_transaction_db(
    session: AsyncSession,
    user_trader_db_with_sbp: UserModel,
) -> BlockchainTransactionModel:
    """Добавить транзакцию в БД."""

    transaction = BlockchainTransactionModel(
        user_id=user_trader_db_with_sbp.id,
        to_address="*" * 42,  # тестовая строка с нужной длиной
        amount=100,
        type=TransactionTypeEnum.PAY_IN,
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)

    return transaction


@pytest_asyncio.fixture
async def blockchain_transaction_pay_out_db(
    session: AsyncSession,
    user_trader_db_with_sbp: UserModel,
) -> BlockchainTransactionModel:
    """Добавить транзакцию в БД."""

    transaction = BlockchainTransactionModel(
        user_id=user_trader_db_with_sbp.id,
        from_address="*" * 42,  # тестовая строка с нужной длиной
        to_address="*" * 42,  # тестовая строка с нужной длиной
        amount=100,
        type=TransactionTypeEnum.PAY_OUT,
    )
    session.add(transaction)
    await session.commit()

    return transaction


# MARK: Transactions
@pytest_asyncio.fixture
async def transaction_db(
    session: AsyncSession,
    user_merchant_db: UserModel,
) -> TransactionModel:
    """Добавить транзакцию в БД."""

    transaction_db = TransactionModel(
        merchant_id=user_merchant_db.id,
        amount=100,
        type=TransactionTypeEnum.PAY_IN,
        payment_method=TransactionPaymentMethodEnum.CARD,
    )
    session.add(transaction_db)
    await session.commit()

    return transaction_db


@pytest_asyncio.fixture
async def transaction_merchant_pay_in_db(
    session: AsyncSession,
    user_merchant_db: UserModel,
    user_trader_db_with_sbp: UserModel,
) -> TransactionModel:
    """Добавить транзакцию в БД, которую обрабатывает трейдер."""

    transaction_db = TransactionModel(
        merchant_id=user_merchant_db.id,
        trader_id=user_trader_db_with_sbp.id,
        amount=100,
        type=TransactionTypeEnum.PAY_IN,
        payment_method=TransactionPaymentMethodEnum.CARD,
        status=TransactionStatusEnum.SUCCESS,
    )
    session.add(transaction_db)
    await session.commit()

    return transaction_db


@pytest_asyncio.fixture
async def transaction_merchant_pending_pay_in_db(
    session: AsyncSession,
    user_merchant_db: UserModel,
    user_trader_db_with_sbp: UserModel,
) -> TransactionModel:
    """Добавить транзакцию в БД, которую обрабатывает трейдер."""

    transaction_db = TransactionModel(
        merchant_id=user_merchant_db.id,
        trader_id=user_trader_db_with_sbp.id,
        amount=100,
        type=TransactionTypeEnum.PAY_IN,
        payment_method=TransactionPaymentMethodEnum.CARD,
    )
    session.add(transaction_db)
    await session.commit()

    return transaction_db


@pytest.fixture
def merchant_pay_out_create_data() -> merchant_schemas.MerchantPayOutRequestSchema:
    return merchant_schemas.MerchantPayOutRequestSchema(
        amount=100,
        payment_method=TransactionPaymentMethodEnum.CARD,
        full_name=faker.word(),
        card_number=faker.word(),
    )


@pytest.fixture
def transaction_create_data(
    user_merchant_db: UserModel,
) -> transaction_schemas.TransactionCreateSchema:
    return transaction_schemas.TransactionCreateSchema(
        merchant_id=user_merchant_db.id,
        amount=100,
        type=TransactionTypeEnum.PAY_IN,
        payment_method=TransactionPaymentMethodEnum.CARD,
    )


@pytest.fixture
def transaction_update_data(
    user_trader_db_with_sbp: UserModel,
) -> transaction_schemas.TransactionUpdateSchema:
    """Подготовленные данные для обновления транзакции в БД."""

    return transaction_schemas.TransactionUpdateSchema(
        merchant_id=user_trader_db_with_sbp.id,
    )


# MARK: Requisites
@pytest_asyncio.fixture
async def requisite_trader_db(
    session: AsyncSession,
    user_trader_db_with_sbp: UserModel,
) -> RequisiteModel:
    """Добавить реквизит в БД."""

    return await RequisiteRepository.create(
        session=session,
        obj_in={
            "user_id": user_trader_db_with_sbp.id,
            "full_name": faker.word(),
            "phone_number": faker.phone_number(),
            "bank_name": faker.word(),
        },
    )


@pytest.fixture
def requisite_trader_create_data() -> requisite_schemas.RequisiteCreateSchema:
    """Подготовленные данные для создания реквизита в БД."""

    return requisite_schemas.RequisiteCreateSchema(
        full_name=faker.word(),
        phone_number=faker.word(),
        bank_name=faker.word(),
    )


@pytest.fixture
def requisite_admin_create_data(
    user_trader_db_with_sbp: UserModel,
) -> requisite_schemas.RequisiteCreateAdminSchema:
    """Подготовленные данные для создания реквизита в БД администратором."""

    return requisite_schemas.RequisiteCreateAdminSchema(
        user_id=user_trader_db_with_sbp.id,
        full_name=faker.word(),
        phone_number=faker.phone_number(),
        bank_name=faker.word(),
    )


@pytest.fixture
def requisite_trader_update_data() -> requisite_schemas.RequisiteUpdateSchema:
    """Подготовленные данные для обновления реквизита в БД."""

    return requisite_schemas.RequisiteUpdateSchema(
        full_name=faker.word(),
    )


@pytest.fixture
def requisite_admin_update_data(
    user_admin_db: UserModel,
) -> requisite_schemas.RequisiteUpdateAdminSchema:
    """Подготовленные данные для обновления реквизита в БД администратором."""

    return requisite_schemas.RequisiteUpdateAdminSchema(
        user_id=user_admin_db.id,
        full_name=faker.word(),
    )


# MARK: Disputes
@pytest_asyncio.fixture
async def dispute_db(
    session: AsyncSession,
    transaction_merchant_pay_in_db: TransactionModel,
) -> DisputeModel:
    """Добавить диспут в БД."""

    return await DisputeRepository.create(
        session=session,
        obj_in=dispute_schemas.DisputeCreateSchema(
            transaction_id=transaction_merchant_pay_in_db.id,
            description=faker.word(),
            image_urls=[faker.image_url()],
        ),
    )


@pytest.fixture
def dispute_create_data(
    transaction_merchant_pay_in_db: TransactionModel,
) -> dispute_schemas.DisputeCreateSchema:
    """Подготовленные данные для создания диспута в БД."""

    return dispute_schemas.DisputeCreateSchema(
        transaction_id=transaction_merchant_pay_in_db.id,
        description=faker.word(),
        image_urls=[faker.image_url()],
    )


@pytest.fixture
def dispute_update_data(
    user_trader_db_with_sbp: UserModel,
) -> dispute_schemas.DisputeUpdateSchema:
    """Подготовленные данные для обновления диспута в БД."""

    return dispute_schemas.DisputeUpdateSchema(
        accept=False,
        description=faker.word(),
    )


@pytest.fixture
def dispute_support_update_data(
    user_trader_db_with_sbp: UserModel,
) -> dispute_schemas.DisputeSupportUpdateSchema:
    """Подготовленные данные для обновления диспута в БД суппортом."""

    return dispute_schemas.DisputeSupportUpdateSchema(
        winner_id=user_trader_db_with_sbp.id,
        description=faker.word(),
    )
