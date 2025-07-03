# Monitoring Project

This is the main Django project for the monitoring backend. It configures the core settings, API routing, and background task scheduling for the monitoring system.

## Project Structure

- **settings.py**: Main Django settings, including environment variable loading, installed apps, middleware, database config, REST framework, and Celery settings.
- **urls.py**: Root URL configuration. Routes:
  - `/admin/`: Django admin site
  - `/api/v1/accounts/`: User registration and authentication (accounts app)
  - `/api/v1/`: Network and host management (network app)
- **celery.py**: Celery app configuration. Sets up periodic tasks for host pinging and data submission.
- **wsgi.py**: WSGI entrypoint for deployment.
- **asgi.py**: ASGI entrypoint for async servers.

## Configuration

- **Environment Variables**: Loaded from a `.env` file if present. Key variables include:
  - `CLOUD_API_URL`: Base URL for the cloud API
  - `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`: Security and CORS settings
  - `CELERY_BROKER_URL`: URL for the Celery broker (e.g., Redis)
- **Custom User Model**: Uses `accounts.CustomUser` as the user model.
- **REST Framework**: Uses token authentication by default.

## Celery Integration

- **celery.py** configures Celery and schedules two periodic tasks:
  - `ping_hosts`: Runs every 60 seconds to ping all hosts
  - `submit_ping_data`: Runs every 5 minutes to aggregate and send ping data to the cloud API
- Celery tasks are discovered from all installed apps.

## API Routing

- All API endpoints are versioned under `/api/v1/`.
- The `accounts` app handles user registration and login.
- The `network` app handles network and host CRUD operations and monitoring.

## Deployment

- The project is ready for deployment with WSGI or ASGI servers.
- Docker and docker-compose files are provided for local and production deployments.
