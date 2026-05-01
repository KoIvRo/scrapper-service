# Bot-Service

Telegram бот для управления отслеживаемыми ссылками. Взаимодействует с пользователем и отправляет запросы в Scrapper-Service.

## Использование

Проект запускается файлом main.py из директории src

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

- **Aiogram**
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **HTTPX**
- **Pytest**
- **Pytest-asyncio**
- **confluent-kafka**

### Классы

Классы связаны между собой абстракциями, в которые вынесен необходимый функционал. Не зависят от реализации друг друга.

### Свзяь между сервисами

Сервисы могут общаться через HTTP или Kafka:
- `Bot-Service` получает команды от пользователя в Telegram.
- `Bot-Service` отправляет запросы к API или отправляет сообщения в kafka
- `Scrapper-Service` самостоятельно опрашивает внешние ресурсы (GitHub, StackOverflow) по расписанию и отправляет уведомления.

## Тестирование

Написаны unit тесты на все обработчики команд, вызовы Scrapper API замоканы.

Для запуска выполните `pytest tests`
