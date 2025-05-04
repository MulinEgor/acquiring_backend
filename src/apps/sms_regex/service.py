from src.apps.sms_regex import schemas
from src.apps.sms_regex.model import SmsRegexModel
from src.apps.sms_regex.repository import SmsRegexRepository
from src.lib.base.service import BaseService


class SmsRegexService(
    BaseService[
        SmsRegexModel,
        schemas.SmsRegexCreateSchema,
        schemas.SmsRegexGetSchema,
        schemas.SmsRegexPaginationSchema,
        schemas.SmsRegexListGetSchema,
        schemas.SmsRegexUpdateSchema,
    ],
):
    repository: SmsRegexRepository = SmsRegexRepository()
    not_found_exception_message = "Регулярные выражения не найдены."
    conflict_exception_message = "Возник конфликт при создании регулярного выражения."
