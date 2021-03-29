# Georgebot
Georgebot is simple crypto trading bot written in Python. It is designed to support only Deribit exchange. The task for this bot is https://algalon.com/static/algalon_developer_test_ru.pdf

## Configuration
Add  `client_id` and `client_secret` from Deribit API in file `conf\conf.yaml`. Change another parameters as you wish.

## How to run
1. build docker image
```
docker build -t georgebot .
```

2. run docker image
```
docker run georgebot
```

## Requirements
- python 3+
- docker
- poetry
- asyncio
- websockets
- PyYAML
- peewee