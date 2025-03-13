"""Основной модуль для конфигурации FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.auth import auth_router
from src.constants import CORS_HEADERS, CORS_METHODS
from src.healthcheck import health_check_router
from src.settings import settings
from src.users import user_router

app = FastAPI(
    title="FastAPI Template",
    version=settings.APP_VERSION,
)


app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)


available_routers = [
    health_check_router,
    auth_router,
    user_router,
]

for router in available_routers:
    app.include_router(router=router, prefix="/api/v1")


@app.get(
    path="/",
    response_class=HTMLResponse,
    tags=["Домашняя страница с ссылками на документацию"],
)
def home():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FastAPI Auth Template</title>
    </head>
    <body>
        <h1>FastAPI Auth Template in {settings.MODE} mode</h1>
        <ul>
            <li><a href="/docs">Документация Swagger</a></li>
            <li><a href="/redoc">Документация ReDoc</a></li>
        </ul>
    </body>
    </html>
    """
