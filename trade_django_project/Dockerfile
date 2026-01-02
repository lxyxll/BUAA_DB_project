FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y gcc default-libmysqlclient-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=tradeDjango.settings

RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "tradeDjango.wsgi:application", "-b", "0.0.0.0:8000", "--workers=3"]
