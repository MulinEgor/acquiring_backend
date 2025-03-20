# Запуск и остановка сервисов
build:
	docker compose --profile dev down -v; \
	docker compose --profile dev build; \
	$(MAKE) start; \
	$(MAKE) migrate
start:
	docker compose --profile dev up -d
stop:
	docker compose --profile dev down
# Запуск тестов
test:
	@EXIT_CODE=0; \
	docker compose -f docker-compose.yml run --rm api-test || EXIT_CODE=$$?; \
	docker compose -f docker-compose.yml --profile test down --volumes; \
	exit $$EXIT_CODE
# Миграции
migrate:
	docker compose exec admin-api alembic upgrade head
# Исправление и проверка кода линтером
ruff_fix: 
	uv run ruff format . && uv run ruff check --fix . && uv run ruff check --fix --select I .
ruff_check:
	uv run ruff format --check . && uv run ruff check . && uv run ruff check --select I .
