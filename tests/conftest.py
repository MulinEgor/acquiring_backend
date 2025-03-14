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

import src.auth.schemas as auth_schemas
import src.users.schemas as user_schemas
from src.auth.services.jwt_service import JWTService
from src.permissions import schemas as permission_schemas
from src.permissions.models import PermissionModel
from src.roles import schemas as role_schemas
from src.roles.models import RoleEnum, RoleModel
from src.settings import settings
from src.users.models import UserModel
from src.utils import hash as utils

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
async def task_session(
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


# MARK: Roles
@pytest_asyncio.fixture
async def role_merchant_db(session: AsyncSession) -> RoleModel:
    """Добавить роль merchant в БД."""

    role_merchant = RoleModel(
        id=str(uuid.uuid4()),
        name=RoleEnum.MERCHANT,
    )
    session.add(role_merchant)
    await session.commit()

    return role_merchant


@pytest_asyncio.fixture
async def role_trader_db(session: AsyncSession) -> RoleModel:
    """Добавить роль trader в БД."""

    role_trader = RoleModel(
        id=str(uuid.uuid4()),
        name=RoleEnum.TRADER,
    )
    session.add(role_trader)
    await session.commit()

    return role_trader


@pytest_asyncio.fixture
async def role_support_db(session: AsyncSession) -> RoleModel:
    """Добавить роль support в БД."""

    role_support = RoleModel(
        id=str(uuid.uuid4()),
        name=RoleEnum.SUPPORT,
    )
    session.add(role_support)
    await session.commit()

    return role_support


@pytest_asyncio.fixture
async def role_admin_db(session: AsyncSession) -> RoleModel:
    """Добавить роль admin в БД."""

    role_admin = RoleModel(
        id=str(uuid.uuid4()),
        name=RoleEnum.ADMIN,
    )
    session.add(role_admin)
    await session.commit()

    return role_admin


@pytest.fixture
def role_create_data() -> role_schemas.RoleCreateSchema:
    """Подготовленные данные для создания роли в БД."""

    return role_schemas.RoleCreateSchema(
        name=faker.word(),
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


@pytest_asyncio.fixture
async def permission_create_data() -> permission_schemas.PermissionCreateSchema:
    """Подготовленные данные для создания разрешения в БД."""

    return permission_schemas.PermissionCreateSchema(
        name=faker.word(),
    )


# MARK: Users
@pytest_asyncio.fixture
async def user_db(session: AsyncSession, role_merchant_db: RoleModel) -> UserModel:
    """Добавить пользователя в БД."""

    user_db = UserModel(
        id=str(uuid.uuid4()),
        email=faker.email(),
        hashed_password=utils.get_hash(faker.password()),
        role_id=role_merchant_db.id,
    )
    session.add(user_db)
    await session.commit()

    return user_db


@pytest_asyncio.fixture
async def user_admin_db(
    session: AsyncSession,
    role_admin_db: RoleModel,
) -> UserModel:
    """Добавить пользователя-администратора в БД."""

    user_admin = UserModel(
        id=str(uuid.uuid4()),
        email=faker.email(),
        hashed_password=utils.get_hash(faker.password()),
        role_id=role_admin_db.id,
    )
    session.add(user_admin)
    await session.commit()

    return user_admin


@pytest_asyncio.fixture
async def user_create_data(
    role_merchant_db: RoleModel,
) -> user_schemas.UserCreateSchema:
    """
    Подготовленные данные для создания
    пользователя в БД администратором.
    """

    return user_schemas.UserCreateSchema(
        email=faker.email(),
        role_name=role_merchant_db.name,
    )


@pytest_asyncio.fixture
async def user_update_data(
    role_merchant_db: RoleModel,
) -> user_schemas.UserUpdateSchema:
    """
    Подготовленные данные для обновления
    пользователя в БД администратором.
    """

    return user_schemas.UserUpdateSchema(
        email=faker.email(),
        password=faker.password(),
        role_name=role_merchant_db.name,
    )


@pytest_asyncio.fixture
async def user_jwt_tokens(user_db: UserModel) -> auth_schemas.JWTGetSchema:
    """Создать JWT токены  для тестового пользователя."""

    return await JWTService.create_tokens(user_id=user_db.id)


@pytest_asyncio.fixture
async def admin_jwt_tokens(user_admin_db: UserModel) -> auth_schemas.JWTGetSchema:
    """Создать JWT токены  для тестового пользователя-администратора."""

    return await JWTService.create_tokens(user_id=user_admin_db.id)
