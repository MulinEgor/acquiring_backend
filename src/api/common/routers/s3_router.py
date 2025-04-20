from fastapi import APIRouter, Depends, File, UploadFile, status

from src.core import constants, dependencies
from src.lib.services.s3_service import S3Service

router = APIRouter(prefix="/s3", tags=["S3"])


@router.post(
    "",
    summary="Загрузить файлы в S3.",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.CREATE_FILE])
        ),
    ],
)
async def upload_files_route(
    files: list[UploadFile] = File(...),
) -> dict[str, list[str]]:
    """
    Загрузка файлов в S3.

    Требуется разрешение: `создать файл`.
    """
    return {"file_urls": await S3Service.upload_bulk(files)}


@router.get(
    "",
    summary="Получить список всех файлов в S3.",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            dependencies.check_user_permissions([constants.PermissionEnum.GET_FILE])
        ),
    ],
)
async def get_all_files_route() -> dict[str, list[str]]:
    """
    Получение списка всех файлов в S3.

    Требуется разрешение: `получить файл`.
    """
    return {"file_urls": await S3Service.get_all()}
