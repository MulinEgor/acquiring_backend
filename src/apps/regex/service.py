from src.apps.regex import schemas
from src.apps.regex.model import RegexModel
from src.apps.regex.repository import RegexRepository
from src.libs.base.service import BaseService


class RegexService(
    BaseService[
        RegexModel,
        schemas.RegexCreateSchema,
        schemas.RegexGetSchema,
        schemas.RegexPaginationSchema,
        schemas.RegexListGetSchema,
        schemas.RegexUpdateSchema,
    ],
):
    repository: RegexRepository = RegexRepository()
    not_found_exception_message = "Регулярные выражения не найдены."
    conflict_exception_message = "Возник конфликт при создании регулярного выражения."
