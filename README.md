# telegram_bot_template

This is a starting point for implemention of a telegram bot.
It consist of 4 services:
- Bot service: Business logic of application
- Postgres: Database
- PgAdmin: Administration of Database
- Minio: Storage for files

# Getting started
Create `.env` file and add a TOKEN from https://t.me/BotFather
```
TOKEN="Your secret token"
POSTGRES_USER="postgresuser"
POSTGRES_PASSWORD="postgrespass"
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
