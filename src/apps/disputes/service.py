"""Модуль для сервисов диспутов."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.disputes import schemas
from src.apps.disputes.model import DisputeModel, DisputeStatusEnum
from src.apps.disputes.repository import DisputeRepository
from src.apps.transactions.model import TransactionStatusEnum
from src.apps.transactions.repository import TransactionRepository
from src.apps.transactions.service import TransactionService
from src.apps.users.model import UserModel
from src.apps.users.repository import UserRepository
from src.core import constants, exceptions
from src.lib.base.service import BaseService


class DisputeService(
    BaseService[
        DisputeModel,
        schemas.DisputeCreateSchema,
        schemas.DisputeGetSchema,
        schemas.DisputeSupportPaginationSchema,
        schemas.DisputeListSchema,
        schemas.DisputeSupportUpdateSchema,
    ],
):
    """Сервис для работы с диспутами."""

    repository = DisputeRepository

    # MARK: Get
    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        id: int,
        user_id: int | None = None,
    ) -> schemas.DisputeGetSchema:
        """
        Получить диспут по ID.

        Args:
            session (AsyncSession): Сессия БД.
            id (int): Идентификатор диспута.
            user_id (int | None): Идентификатор пользователя.

        Returns:
            DisputeGetSchema: Схема для получения диспута.

        Raises:
            NotFoundException: Диспут не найден.
        """

        dispute_db = await cls.repository.get_one_or_none(
            session=session,
            id=id,
        )
        if not dispute_db:
            raise exceptions.NotFoundException("Диспут не найден")

        if user_id:
            transaction_db = await TransactionRepository.get_one_or_none(
                session=session,
                id=dispute_db.transaction_id,
            )
            if not transaction_db:
                raise exceptions.NotFoundException("Транзакция не найдена")

            if (
                transaction_db.merchant_id != user_id
                and transaction_db.trader_id != user_id
            ):
                raise exceptions.NotFoundException("Диспут не принадлежит пользователю")

        return dispute_db

    # MARK: Create
    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        data: schemas.DisputeCreateSchema,
        merchant_db: UserModel,
    ) -> schemas.DisputeGetSchema:
        """
        Создать диспут.

        Получение транзакции, проверка ее статуса(она должна быть завершена),
        Заморозка счета трейдера, перевод транзакции в статус 'в процессе рассмотрения',
        Создание диспута в БД.

        Args:
            session (AsyncSession): Сессия БД.
            data (DisputeCreateSchema): Схема для создания диспута.
            merchant_db (UserModel): Модель мерчанта.

        Returns:
            DisputeGetSchema: Схема для получения диспута.

        Raises:
            NotFoundException: Транзакция не найдена.
            ConflictException: Транзакция не завершена или не принадлежит пользователю.
        """

        # Получение и проверка транзакции
        transaction = await TransactionService.get_by_id(
            session=session, id=data.transaction_id
        )
        if transaction.status != TransactionStatusEnum.SUCCESS:
            raise exceptions.ConflictException(
                "Транзакция должна быть завершена, чтобы создать диспут"
            )
        elif transaction.merchant_id != merchant_db.id:
            raise exceptions.ConflictException("Эта транзакция не принадлежит вам")

        # Изменение статуса транзакции
        transaction.status = TransactionStatusEnum.DISPUTED

        # Заморозка средств на счете трейдера
        trader_db = await UserRepository.get_one_or_none(
            session=session, id=transaction.trader_id
        )
        trader_db.amount_frozen += transaction.amount

        # Создание диспута в БД
        data = {
            "description": f"Мерчант: {data.description}",
            **data.model_dump(),
        }
        dispute = await super().create(session=session, data=data)

        return dispute

    # MARK: Update
    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        id: int,
        data: schemas.DisputeUpdateSchema,
        trader_db: UserModel,
    ) -> None:
        """
        Обновить диспут.

        Если трейдер принимает вину, то средства списываються с его счета
        с учетом штрафа, и баланс мерчанта пополняется с учетом комиссии,
        диспут закрывается и транзакция возвращается в статус 'завершена'.

        Если трейдер не принимает вину, то диспут остается открытым,
        и финальное решение принимается поддержкой.

        Args:
            session (AsyncSession): Сессия БД.
            id (int): Идентификатор диспута.
            data (DisputeUpdateSchema): Схема для обновления диспута.
            trader_db (UserModel): Модель трейдера.

        Raises:
            NotFoundException: Диспут не найден.
            ConflictException: Диспут не принадлежит пользователю.
        """

        dispute_db = await cls.repository.get_one_or_none(session=session, id=id)
        if not dispute_db:
            raise exceptions.NotFoundException("Диспут не найден")
        elif dispute_db.transaction.trader_id != trader_db.id:
            raise exceptions.ConflictException("Этот диспут не принадлежит вам")

        transaction_db = await TransactionRepository.get_one_or_none(
            session=session, id=dispute_db.transaction_id
        )

        # Обновление описания и изображений
        if data.description:
            dispute_db.description += f"\nТрейдер: {data.description}"
        if data.image_urls:
            dispute_db.image_urls.extend(data.image_urls)

        # Трейдер принимает вину
        if data.accept:
            # Списание средств с трейдера
            trader_db.amount_frozen -= transaction_db.amount
            trader_db.balance -= (
                transaction_db.amount
                + transaction_db.amount * constants.TRADER_DISPUTE_PENALTY
            )

            # Пополнение баланса мерчанта
            merchant_db = await UserRepository.get_one_or_none(
                session=session, id=transaction_db.merchant_id
            )
            merchant_db.balance += (
                transaction_db.amount
                - transaction_db.amount * constants.MERCHANT_COMMISSION
            )

            # Закрытие диспута и транзакции
            dispute_db.status = DisputeStatusEnum.CLOSED
            transaction_db.status = TransactionStatusEnum.SUCCESS

        await session.commit()

    @classmethod
    async def update_by_support(
        cls,
        session: AsyncSession,
        id: int,
        data: schemas.DisputeSupportUpdateSchema,
    ) -> None:
        """
        Вынести решение по диспуту поддержкой.

        Если победитель трейдер, то деньги не вычитаются с его счета.
        Если победитель мерчант, то его баланс пополняется с учетом комиссии,
        деньги с трейдера списываются.
        Транзакция возвращается в статус 'завершена',
        и диспут закрывается.

        Args:
            session (AsyncSession): Сессия БД.
            id (int): Идентификатор диспута.
            data (DisputeSupportUpdateSchema): Схема для обновления диспута.

        Raises:
            NotFoundException: Диспут не найден.
            ConflictException: Диспут не находится в процессе рассмотрения,
                победитель не является ни трейдером, ни мерчантом.
        """

        dispute_db = await cls.repository.get_one_or_none(session=session, id=id)
        if not dispute_db:
            raise exceptions.NotFoundException("Диспут не найден")
        elif dispute_db.status != DisputeStatusEnum.PENDING:
            raise exceptions.ConflictException(
                "Диспут не находится в процессе рассмотрения"
            )

        transaction_db = await TransactionRepository.get_one_or_none(
            session=session, id=dispute_db.transaction_id
        )
        trader_db = await UserRepository.get_one_or_none(
            session=session, id=transaction_db.trader_id
        )

        if data.winner_id == dispute_db.transaction.trader_id:
            trader_db.amount_frozen -= transaction_db.amount
        elif data.winner_id == dispute_db.transaction.merchant_id:
            # Пополнение баланса мерчанта
            merchant_db = await UserRepository.get_one_or_none(
                session=session, id=transaction_db.merchant_id
            )
            merchant_db.balance += (
                transaction_db.amount
                - transaction_db.amount * constants.MERCHANT_COMMISSION
            )

            # Списание средств с трейдера
            trader_db.amount_frozen -= transaction_db.amount
            trader_db.balance -= (
                transaction_db.amount
                + transaction_db.amount * constants.TRADER_DISPUTE_PENALTY
            )
        else:
            raise exceptions.ConflictException(
                "Победитель не является ни трейдером, ни мерчантом"
            )

        # Закрытие диспута и транзакции
        dispute_db.status = DisputeStatusEnum.CLOSED
        transaction_db.status = TransactionStatusEnum.SUCCESS
        dispute_db.winner_id = data.winner_id

        await session.commit()
