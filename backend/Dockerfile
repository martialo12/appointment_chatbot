FROM python:3.9.9-slim-buster as base
FROM base as dev

ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV PORT=8090

WORKDIR /app

RUN apt update && \
    apt install -y postgresql-client

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD uvicorn app.application:app --host ${HOST} --port ${PORT} --reload
