# Бэкенд для системы эквайринга

[![Static Badge](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org)
[![Static Badge](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Static Badge](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)](https://swagger.io)
[![Static Badge](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Static Badge](https://img.shields.io/badge/-SQLAlchemy-ffd54?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Static Badge](https://img.shields.io/badge/docker-257bd6?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)


## Тесты (необязательно, но лучше запустить, чтобы убедиться в работаспособности)
1. Перед запуском тестов необходимо создать `.env.test` на основе`.env.test.example`:
```bash
cp -r .env.test.example .env.test
```

2. Запустить тесты:
```bash
make test
```


## Запуск проекта
1. Создать `.env` на основании `.env.example`:
```bash
cp -r .env.example .env
```

2. Запустить API и БД в Docker контейнерах:
```bash
make start
```

3. Применить миграции:
```bash
make migrate
```

4. Документация API и доступные эндпоинты:
## Админка: http://localhost:80/docs
## Основное API: http://localhost:81/docs

5. Для остановки контейнеров выполнить
```bash
make stop
```

## Тестовые данные для входа

email: admin@gmail.com
password: admin
