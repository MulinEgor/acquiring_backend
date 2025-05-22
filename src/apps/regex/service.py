from src.apps.regex import constants, schemas
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
    not_found_exception_message, not_found_exception_code = (
        constants.NOT_FOUND_EXCEPTION_MESSAGE,
        constants.NOT_FOUND_EXCEPTION_CODE,
    )
    conflict_exception_message, conflict_exception_code = (
        constants.CONFLICT_EXCEPTION_MESSAGE,
        constants.CONFLICT_EXCEPTION_CODE,
    )
