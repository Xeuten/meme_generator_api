FROM python:3.12.7-slim

RUN pip install poetry

WORKDIR /app

COPY . .

RUN poetry install --no-root --no-interaction --no-ansi

ENTRYPOINT poetry run poe syncdb \
    && poetry run python manage.py createsuperuser --noinput --email "$DJANGO_SUPERUSER_EMAIL" || true \
    && poetry run python manage.py shell -c \
    "import os;\
    from api.models import User;\
    user = User.objects.filter(email=os.environ['DJANGO_SUPERUSER_EMAIL']).first();\
    user.set_password(os.environ['DJANGO_SUPERUSER_PASSWORD']);\
    user.save();"\
    && poetry run python manage.py test --noinput \
    && poetry run poe dev
