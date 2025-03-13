FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:0.5.7 /uv /uvx /bin/

COPY . /app

WORKDIR  /app

ARG ENV

# Если `ENV=build`, не устанавливать зависимости dev (нужны только для разработки и тестов).
# В противном случае установить все зависимости.

RUN if [ "$ENV" = "build" ]; then \
      uv sync --no-dev; \
    else \
      uv sync --all-groups --link-mode=copy; \
    fi

ENV PATH="/app/.venv/bin:$PATH"
