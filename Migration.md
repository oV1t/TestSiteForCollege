Змініть ваші моделі у файлі backend/models.py.
Згенеруйте нову міграцію (Alembic порівняє код із базою та створить файл):

docker exec fastapi_app alembic revision --autogenerate -m "опис змін, наприклад: add user phone"

docker exec fastapi_app alembic revision --autogenerate -m "опис змін, наприклад: add user phone"
Застосуйте міграцію (змінить структуру таблиць у БД):

docker exec fastapi_app alembic upgrade head

docker exec fastapi_app alembic upgrade head
🛠️ Додаткові корисні команди:
Перевірити поточний статус міграцій (на якій версії зараз БД):

docker exec fastapi_app alembic current

Подивитися історію міграцій:

docker exec fastapi_app alembic history --verbose

Скасувати останню міграцію (Downgrade):

docker exec fastapi_app alembic downgrade -1

docker exec fastapi_app alembic downgrade -1
Перевірити, чи бачить Alembic зміни (без створення файлу):

docker exec fastapi_app alembic check
