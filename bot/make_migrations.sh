#!/bin/bash

echo "Generating migrations files..."
alembic upgrade head
alembic revision --autogenerate

echo "Applying migrations..."
alembic upgrade head

echo "Migrations done!"
