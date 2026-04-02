# Link Tracker Monorepo

Монорепозиторий, объединяющий Telegram-бота для управления отслеживаемыми ссылками и backend-сервис для отслеживания изменений на GitHub и StackOverflow.

## Структура проекта

```
project/
├── bot/                  # Telegram бот (Bot-Service)
│   ├── src/              # Исходный код бота
│   └── tests/            # Тесты для бота
├── scrapper/             # Backend сервис (Scrapper-Service)
│   ├── src/              # Исходный код scrapper-сервиса
│   ├── tests/            # Тесты для scrapper-сервиса
│   └── migrations/       # SQL миграции для базы данных
└── docker-compose.yml    # Файл для запуска всей инфраструктуры
```

## Быстрый старт

### Запуск с помощью Docker (рекомендуемый способ)

1. Создайте файл `.env` в директории `bot/src/secrets/.env` и `scrapper/src/secrets/.env`, используя примеры `.env_example` в соответствующих папках.
2. Из корня проекта выполните команду:

```bash
docker-compose up --build
```

### Локальный запуск

1. Убедитесь, что установлен PostgreSQL и он запущен.
2. Создайте и настройте `.env` файлы для обоих сервисов.
3. Запустите каждый сервис отдельно из его директории `src`:

```bash
# Для бота
cd bot/src
python main.py

# Для scrapper-сервиса
cd scrapper/src
python main.py
```

## Сервисы

### Bot-Service

Telegram-бот для управления отслеживаемыми ссылками. Взаимодействует с пользователем и отправляет запросы в Scrapper-Service.

**Используемые библиотеки:**
- Aiogram
- FastAPI (для вебхуков)
- Uvicorn
- Pydantic
- HTTPX

**Основные команды бота:**
- `/track` — диалог добавления ссылки (FSM)
- `/untrack` — удаление ссылки
- `/list [тег]` — список отслеживаемых ссылок с фильтром по тегу

### Scrapper-Service

Backend-сервис, отвечающий за отслеживание изменений на GitHub и StackOverflow.

**Используемые библиотеки:**
- FastAPI
- Uvicorn
- Pydantic
- HTTPX
- asyncpg / sqlalchemy
- Alembic

**Работа с базой данных:**
- Поддерживается PostgreSQL.
- Миграции управляются через Alembic.
- Реализованы два способа доступа к данным:
  - **Raw SQL** — низкоуровневый доступ (`access-type=raw`)
  - **ORM** — высокоуровневый доступ через SQLAlchemy (`access-type=raw`)
- Выбор режима работы задается в конфигурации (файл `.env`).

## Общая архитектура

Сервисы связаны через HTTP:
- `Bot-Service` получает команды от пользователя в Telegram.
- `Bot-Service` отправляет запросы к API `Scrapper-Service` для выполнения CRUD-операций над ссылками и подписками.
- `Scrapper-Service` самостоятельно опрашивает внешние ресурсы (GitHub, StackOverflow) по расписанию и отправляет уведомления.

Ключевые абстракции в обоих сервисах построены так, чтобы классы не зависели от реализации друг друга и обеспечивали типобезопасность.

## Тестирование

### Для обоих сервисов

Тесты написаны с использованием `pytest` и `pytest-asyncio`. Внешние API замоканы в фикстурах.

Запуск тестов для конкретного сервиса:

```bash
# Для бота
cd bot
pytest tests

# Для scrapper-сервиса
cd scrapper
pytest tests
```

### Интеграционное тестирование (Scrapper-Service)

Для `Scrapper-Service` реализованы тесты с использованием `Testcontainers`, которые поднимают реальные экземпляры PostgreSQL и проверяют корректность работы с БД.

Для запуска интеграционных тестов:

```bash
pytest tests
```

Убедитесь что docker запущен

## Конфигурация

Все настройки хранятся в файлах `.env`, которые необходимо создать по примеру `.env_example` в соответствующих директориях `secrets/`.

- **Bot-Service:** `bot/src/secrets/.env`
- **Scrapper-Service:** `scrapper/src/secrets/.env`

**Основные переменные окружения:**
- `BOT_TOKEN` — токен Telegram бота.
- `SCRAPPER_URL` — URL для доступа к API Scrapper-Service.
- `DATABASE_URL` — строка подключения к PostgreSQL (для Scrapper-Service).
- `ACCESS_TYPE` — тип доступа к БД (`raw` или `orm`) (для Scrapper-Service).
