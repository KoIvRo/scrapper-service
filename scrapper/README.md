# Scrapper-Service

Сервис позволяющий отслеживать изменения внесенный в репозиторий github или тему на stackoverflow.

## Использование

Проект запускается файлом main.py из директорий src

```
python main.py
```

### docker

Для запуска всего проекта через докер:

```
project/
    bot/
    srcapper/
        docker-compose.yml
```

```
docker-compose -f docker-compose.yml up --build
```

## ВАЖНО

Не забудьте создать файл .env в src/secrets/.env, пример заполнения можно посмотреть в той же директории.
src/secrets/.env_example

## Документация

### Используемые библиотеки

- **FastAPI**
- **Uvicorn**  
- **Pydantic**
- **HTTPX**
- **Pytest**
- **Pytest-asyncio**
- **Testcontainers**
- **asyncpg**
- **sqlalchemy**
- **Alembic**
- **confluent-kafka**

### Классы

```
FastAPI endpoints -> LinkService -> RawRepository/OrmRepository

Scheduler -> Clients -> Notifier
```

Классы связаны между собой абстракциями, в которые вынесен необходимый функционал. Не зависят от реализации друг друга.

### Работа с базой данный

В этой итерации была добавлена возможность работы с базой данных PostgreSQL. Работа с базой данных осуществленная в классах RawRepository, OrmReposotiry. Выбрать режим работы можно в файле src/secrets/.env.

В задании релизована пагинация на получение ссылок из бд.

По часто используемым атрибутам в бд построенны индексы.

### Свзяь между сервисами

Сервисы могут общаться через HTTP или Kafka:
- `Bot-Service` получает команды от пользователя в Telegram.
- `Bot-Service` отправляет запросы к API или отправляет сообщения в kafka
- `Scrapper-Service` самостоятельно опрашивает внешние ресурсы (GitHub, StackOverflow) по расписанию и отправляет уведомления.

#### Transactional Outbox

Релизован паттерн Transactional Outbox.

В режиме работы kafka Scheduler записывает обновления в outbox таблицу в базе данных. OutboxProcessor берет данные из базы и отправляет уведомления в kafka.

## Тестирование

Написаны unit тесты на все основные функции, все вызовы настоящих api замоканы в фикстурах.

Для запуска выполните `pytest tests`
