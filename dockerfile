FROM python:3.11-alpine

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

COPY ./requirements.txt .

RUN apk update && \
    apk add netcat-openbsd && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

ENTRYPOINT ["/code/entrypoint.sh"]
