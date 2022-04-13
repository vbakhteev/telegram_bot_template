# telegram_bot_template

This is a starting point to implement telegram bot.
It consist of 4 services:
- Bot service: Business logic of application
- Postgres: Database
- PgAdmin: Administration of Database
- Minio: Storage for files

# Getting started
Create `.env` file and add the TOKEN from https://t.me/BotFather
```
TOKEN="Your secret token"
PROD=false
```

### Launch all services:
```
make start
```

### See all commands:
```
make
```