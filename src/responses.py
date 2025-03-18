"""Модуль для ответов от API."""

import orjson
from pydantic import BaseModel
from sanic import json


def api_response(
    data: BaseModel,
    status: int = 200,
    headers: dict | None = None,
    content_type: str = "application/json",
) -> json:
    """
    Ответ на успешный запрос.

    Args:
        data: Данные для ответа.
        status: Статус ответа.
        headers: Заголовки ответа.
        content_type: Тип содержимого ответа.

    Returns:
        Ответ на успешный запрос.
    """

    return json(
        body=orjson.loads(data.model_dump_json()),
        status=status,
        headers=headers,
        content_type=content_type,
    )
