"""Модуль для мидлварей."""

from sanic import Request, Sanic


async def get_db_session_middleware(request: Request):
    """Middleware для получения сессии базы данных в роуте."""
    request.ctx.get_db_session = Sanic.get_app().ctx.get_db_session
