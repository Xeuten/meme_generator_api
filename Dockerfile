FROM python:3.12.7-slim

RUN pip install poetry

WORKDIR /app

COPY . .

RUN poetry install --no-root --no-interaction --no-ansi

ENTRYPOINT poetry run poe syncdb && poetry run poe dev
