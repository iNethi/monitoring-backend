# Monitoring Backend

A Django-based backend API for monitoring local network connectivity and uptime. This project is designed to help users and network administrators track the status of hosts and networks, with automatic reporting to a central cloud API. It is production-ready, supports Docker deployment, and is extensible for custom monitoring needs.

## Features

- User registration and authentication (with cloud API verification)
- CRUD endpoints for networks and hosts
- Periodic pinging of hosts and uptime tracking
- Automatic reporting of ping data to a cloud API
- Celery-based background tasks for reliability and retries
- Centralized logging (file and console, with rotation)
- Docker and docker-compose support for easy deployment
- Automatic superuser creation from environment variables

## Project Structure

- `monitoring/accounts/` – User management, registration, login, and custom user model
- `monitoring/network/` – Network and host models, ping logic, API endpoints, and Celery tasks
- `monitoring/monitoring/` – Project settings, Celery config, and main URL routing

## Quick Start (with Docker)

1. **Clone the repository:**

   ```bash
   git clone <repo-url>
   cd monitoring-backend
   ```

2. **Configure environment variables:**

   - Copy `.env.example` to `.env` and adjust values as needed (especially for the superuser and cloud API).

   ```bash
   cp .env.example .env
   # Edit .env as needed
   ```

3. **Build and start the services:**

   ```bash
   docker compose -f docker-compose-dev.yml up --build
   # or for production
   docker compose -f docker-compose-prod.yml up --build
   ```

4. **Access the API:**
   - The Django API will be available at `http://localhost:8100/` (by default).
   - The admin panel is at `/admin/` (login with the superuser credentials from `.env`).

## Environment Variables

Key variables (see `.env.example` for all):

- `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`: Security and CORS
- `CLOUD_API_URL`: Base URL for the cloud API
- `CELERY_BROKER_URL`: Redis URL for Celery
- `SUPERUSER_USERNAME`, `SUPERUSER_EMAIL`, `SUPERUSER_PASSWORD`: For automatic superuser creation
- `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASS`: Database connection

## How It Works

- On container startup, the entrypoint script:
  1. Waits for the database to be ready
  2. Runs migrations
  3. Creates a Django superuser from environment variables (if not already present)
  4. Starts the Django development server
- Celery workers and beat scheduler can be run as separate services (see docker-compose files)
- All logs are written to both the console and a rotating file (`logs/monitoring.log`)

## API Overview

- User registration and login: `/api/v1/accounts/`
- Network and host management: `/api/v1/networks/`, `/api/v1/hosts/`
- See the `monitoring/accounts/README.md` and `monitoring/network/README.md` for detailed endpoint documentation.

## Contributing

Pull requests and issues are welcome! Please open an issue to discuss major changes or new features.

## License

> [!WARNING]
> Closed-source commercial usage of this code is not permitted with the GPL-3.0. If that license is not compatible with your use case, please contact keeganthomaswhite@gmail.com for queries.
