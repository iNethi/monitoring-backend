#!/bin/sh
set -e

# Wait for DB to be ready
python manage.py wait_for_db

# Run migrations
python manage.py migrate

# Create superuser from env vars (safe to run multiple times)
python manage.py create_superuser_from_env

# Start Django server
python manage.py runserver 0.0.0.0:8000 