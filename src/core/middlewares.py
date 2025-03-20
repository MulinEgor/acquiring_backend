"""Модулья для middlewares"""

import orjson
from fastapi import Request
from fastapi.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware


class ORJSONRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        async def custom_json():
            body = await request.body()
            return await run_in_threadpool(orjson.loads, body)

        request.json = custom_json
        response = await call_next(request)
        return response
