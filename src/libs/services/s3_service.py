import boto3
import orjson
from botocore.config import Config
from fastapi import UploadFile

from src.core import constants, exceptions
from src.core.settings import settings


class S3Service:
    """Сервис для работы с S3."""

    _client = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name="ru-msk-1",
        config=Config(signature_version="s3v4"),
    )

    @classmethod
    def _ensure_bucket_exists(cls) -> None:
        """
        Создает публичный бакет, если он не существует

        Raises:
            InternalServerErrorException: Ошибка при создании бакета
        """
        try:
            cls._client.head_bucket(Bucket=settings.S3_BUCKET_NAME)

        except Exception:
            try:
                cls._client.create_bucket(Bucket=settings.S3_BUCKET_NAME)
                cls._client.put_bucket_policy(
                    Bucket=settings.S3_BUCKET_NAME,
                    Policy=orjson.dumps(constants.S3_PUBLIC_BUCKET_POLICY).decode(
                        "utf-8"
                    ),
                )

            except Exception as e:
                raise exceptions.InternalServerErrorException(
                    f"Ошибка при создании бакета: {str(e)}"
                )

    @classmethod
    async def upload_bulk(cls, files: list[UploadFile]) -> list[str]:
        """
        Загружает файлы в S3 и возвращает их URL

        Args:
            files: Файлы для загрузки

        Returns:
            Список URL файлов

        Raises:
            InternalServerErrorException: Ошибка при загрузке файлов
        """

        cls._ensure_bucket_exists()

        file_urls: list[str] = []

        for file in files:
            try:
                file_content = await file.read()
                cls._client.put_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=file.filename,
                    Body=file_content,
                    ContentType=file.content_type,
                )

                file_urls.append(
                    f"{settings.S3_ENDPOINT.replace('s3', 'localhost')}/"
                    f"{settings.S3_BUCKET_NAME}/{file.filename}"
                )

            except Exception as e:
                raise exceptions.InternalServerErrorException(
                    f"Ошибка при загрузке файла: {str(e)}"
                )

        return file_urls

    @classmethod
    async def get_all(cls) -> list[str]:
        """
        Получает список всех файлов в бакете

        Returns:
            Список URL файлов

        Raises:
            InternalServerErrorException: Ошибка при получении списка файлов
            NotFoundException: Файлы не найдены
        """

        cls._ensure_bucket_exists()

        try:
            response = cls._client.list_objects_v2(Bucket=settings.S3_BUCKET_NAME)
            files: list[str] = []
            if "Contents" in response:
                for obj in response.get("Contents", []):
                    files.append(
                        f"{settings.S3_ENDPOINT.replace('s3', 'localhost')}/"
                        f"{settings.S3_BUCKET_NAME}/{obj.get('Key', '')}"
                    )

            if not files:
                raise exceptions.NotFoundException("Файлы не найдены")

            return files

        except Exception as e:
            raise exceptions.InternalServerErrorException(
                f"Ошибка при получении списка файлов: {str(e)}"
            )
