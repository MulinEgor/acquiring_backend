"""Основной модуль для конфигурации FastAPI."""

from sanic import Sanic

from src import constants, dependencies, middlewares
from src.auth.blueprint import bp as auth_bp
from src.settings import settings
from src.users.blueprint import bp as users_bp

app = Sanic(
    name="payment-service-backend",
)


def setup_dependencies(app: Sanic) -> None:
    """Настроить зависимости для приложения."""
    app.ctx.get_db_session = dependencies.get_db_session


def setup_cors(app: Sanic) -> None:
    """Настроить CORS для приложения."""
    app.config.CORS_ORIGINS = settings.CORS_ORIGINS
    app.config.CORS_METHODS = constants.CORS_METHODS
    app.config.CORS_ALLOW_HEADERS = constants.CORS_HEADERS
    app.config.CORS_SUPPORTS_CREDENTIALS = True


def setup_middlewares(app: Sanic) -> None:
    """Настроить middleware для приложения."""
    app.register_middleware(middlewares.get_db_session_middleware, "request")


def setup_auth(app: Sanic) -> None:
    """Настроить авторизацию по JWT в swagger."""
    app.ext.openapi.add_security_scheme(
        "token",
        "http",
        scheme="bearer",
        location="header",
        bearer_format="JWT",
    )


def setup_blueprints(app: Sanic) -> None:
    """Настроить blueprints для приложения."""
    app.blueprint(users_bp)
    app.blueprint(auth_bp)


def setup_swagger(app: Sanic) -> None:
    """Настроить swagger для приложения."""
    app.config.API_TITLE = "API Documentation"
    app.config.API_VERSION = "1.0.0"

    app.config.API_UI = "swagger"

    app.config.SWAGGER_UI_CONFIGURATION = {
        "docExpansion": "none",
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": 0,
        "displayRequestDuration": False,
        "filter": False,
        "syntaxHighlight": {
            "activate": False,
        },
    }


@app.before_server_start
def setup_app(app: Sanic) -> None:
    """Настроить приложение."""
    setup_cors(app)
    setup_dependencies(app)
    setup_middlewares(app)
    setup_blueprints(app)
    setup_auth(app)
    setup_swagger(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, auto_reload=True)
