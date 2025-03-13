# FastAPI Auth Template

[![Static Badge](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![Static Badge](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Static Badge](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)](https://swagger.io)
[![Static Badge](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Static Badge](https://img.shields.io/badge/-SQLAlchemy-ffd54?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Static Badge](https://img.shields.io/badge/docker-257bd6?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)


## Запуск проекта
1. Установить зависимости (можно использовать pip, но рекомендую uv, он намного быстрее): 

   С помощью pip:
   ```bash
   pip install . 
   ```

   С помощью uv:
   ```bash
   uv sync --group dev
   ```

2. Создать `.env` на основании `.env.example`:

```bash
cp -r .env.example .env
```

3. Запустить API и БД в Docker контейнерах:
```bash
make start_dev
```

4. Применить миграции:
```bash
make migrate
```

5. Документация API и доступные эндпоинт:
* Swagger UI: http://127.0.0.1:8000/docs
* ReDoc: http://127.0.0.1:8000/redoc

6. Для остановки контейнеров выполнить
```bash
make stop_dev
```

## Тесты
1. Перед запуском тестов необходимо создать `.env.test` на основе`.env.test.example`:
```bash
cp -r .env.test.example .env.test
```

2. Тесты запускаются из независимой базы данных Postgres с помощью команды `make test`.
