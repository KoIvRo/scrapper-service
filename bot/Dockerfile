FROM python:3.12-slim AS app

WORKDIR /app

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python - \
    && useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --with main

COPY src /app/src
COPY config.yml /app

USER appuser

CMD ["sh", "-c", "sleep 7 && poetry run python src/main.py"]
