"""Основной модуль `conftest` для всех тестов."""

import asyncio
import sys
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from faker import Faker
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import src.modules.auth.schemas as auth_schemas
import src.modules.users.schemas as user_schemas
import src.modules.wallets.schemas as wallet_schemas
from src.core import constants
from src.core.settings import settings
from src.modules.auth.services.jwt_service import JWTService
from src.modules.blockchain.models import BlockchainTransactionModel, TypeEnum
from src.modules.permissions import schemas as permission_schemas
from src.modules.permissions.models import PermissionModel
from src.modules.permissions.repository import PermissionRepository
from src.modules.services.hash_service import HashService
from src.modules.users.models import UserModel
from src.modules.users_permissions.repository import UsersPermissionsRepository
from src.modules.wallets.models import WalletModel

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
        id=str(uuid.uuid4()),
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

    user_admin = UserModel(
        id=str(uuid.uuid4()),
        email=faker.email(),
        hashed_password=HashService.generate(faker.password()),
    )
    session.add(user_admin)

    await session.commit()

    permissions = await PermissionRepository.get_all(session)
    await UsersPermissionsRepository.create_bulk(
        session=session,
        data=[
            {
                "user_id": user_admin.id,
                "permission_id": permission.id,
            }
            for permission in permissions
        ],
    )

    await session.commit()

    return user_admin


@pytest_asyncio.fixture
async def user_trader_db(
    session: AsyncSession,
) -> UserModel:
    """Добавить пользователя-трейдера в БД."""

    user_trader = UserModel(
        id=str(uuid.uuid4()),
        email=faker.email(),
        hashed_password=HashService.generate(faker.password()),
    )
    session.add(user_trader)

    await session.commit()

    trader_permissions = [
        constants.PermissionEnum.REQUEST_PAY_IN_TRADER,
        constants.PermissionEnum.CONFIRM_PAY_IN_TRADER,
    ]
    permissions = await PermissionRepository.get_all(session)
    await UsersPermissionsRepository.create_bulk(
        session=session,
        data=[
            {
                "user_id": user_trader.id,
                "permission_id": permission.id,
            }
            for permission in permissions
            if permission.name in trader_permissions
        ],
    )

    await session.commit()

    return user_trader


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


@pytest_asyncio.fixture
async def user_jwt_tokens(user_db: UserModel) -> auth_schemas.JWTGetSchema:
    """Создать JWT токены  для тестового пользователя."""

    return await JWTService.create_tokens(user_id=user_db.id)


@pytest_asyncio.fixture
async def admin_jwt_tokens(user_admin_db: UserModel) -> auth_schemas.JWTGetSchema:
    """Создать JWT токены  для тестового пользователя-администратора."""

    return await JWTService.create_tokens(user_id=user_admin_db.id)


@pytest_asyncio.fixture
async def trader_jwt_tokens(user_trader_db: UserModel) -> auth_schemas.JWTGetSchema:
    """Создать JWT токены  для тестового пользователя-трейдера."""

    return await JWTService.create_tokens(user_id=user_trader_db.id)


# MARK: Wallets
@pytest_asyncio.fixture
async def wallet_db(session: AsyncSession) -> WalletModel:
    """Добавить кошелек в БД."""

    wallet = WalletModel(
        address="*" * 42,  # тестовая строка с нужной длинойs
    )
    session.add(wallet)
    await session.commit()

    return wallet


@pytest.fixture
def wallet_create_data() -> wallet_schemas.WalletCreateSchema:
    """Подготовленные данные для создания кошелька в БД."""

    return wallet_schemas.WalletCreateSchema(
        address="*" * 42,  # тестовая строка с нужной длинойs
    )


# MARK: Blockchain transactions
@pytest_asyncio.fixture
async def blockchain_transaction_db(
    session: AsyncSession,
    user_trader_db: UserModel,
) -> BlockchainTransactionModel:
    """Добавить транзакцию в БД."""

    transaction = BlockchainTransactionModel(
        user_id=user_trader_db.id,
        to_address="*" * 42,  # тестовая строка с нужной длиной
        amount=100,
        type=TypeEnum.PAY_IN,
    )
    session.add(transaction)
    await session.commit()

    return transaction
