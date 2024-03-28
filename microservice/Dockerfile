FROM python:3.10.11-alpine

ENV PYTHONUNBUFFERED 1

RUN mkdir /notification_microservice

WORKDIR /notification_microservice

COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev && \
    pip install -r requirements.txt && \
    apk del gcc musl-dev

COPY . .

EXPOSE 8001

CMD ["daphne", "-b", "0.0.0.0", "-p", \
     "8001", "config.asgi:application"]

