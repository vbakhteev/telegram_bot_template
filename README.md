# telegram_bot_template

This repo contains boilerplate code and infrastructure provisioning for development of telegram bot.

## Services
- Bot: Entrypoint and business logic of application
- Postgres: Database
- Minio: Storage for different files (images, videos, pdf, etc.)
- PgAdmin: Administration of Postgres
- Grafana: Visualization of application metrics

## Automation
- Infrastructure: All services reside inside docker containers and managed by docker-compose.
- Database migrations: New migrations are created and applied by SqlAlchemy and alembic.
- Grafana: Datasource and dashboard are provisioned with YAML files.

# Getting started
Create `.env` file and add a bot TOKEN from https://t.me/BotFather
```
TOKEN="Your secret token"
POSTGRES_USER="postgresuser"
POSTGRES_PASSWORD="postgrespass"
MINIO_ROOT_USER="minio"
MINIO_ROOT_PASSWORD="minio123"
PROD=false
```

Create volume for Grafana
```
make volume
```

### Launch all services:
```
make start
```

### See all commands:
```
make
```

# Monitoring

- Grafana: http://localhost:3000
- Minio console: http://localhost:9001
- PgAdmin: http://localhost:5050
