ARG PYTHON_VERSION=3.12-slim

FROM python:${PYTHON_VERSION}

RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rv /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

ENV DATABASE_URL "sqlite://:memory:"
ENV SECRET_KEY "MtXleNkOw1Dh8OQAK5TMZ7lWsXJsDqz0U4RjYPPr9AEa16QdVg"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn","--bind",":8000","--workers","2","backend.wsgi"]
