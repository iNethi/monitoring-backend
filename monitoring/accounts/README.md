# Accounts App

This app handles user registration, authentication, and user management for the monitoring backend.

## Endpoints

All endpoints are prefixed with `/api/v1/accounts/` in the main project.

### POST `/register/`

- **Description:** Register a new user. Credentials are verified against the cloud API. If successful, a local user is created and both a cloud and local token are returned.
- **Request Body:**
  - `username`: string
  - `password`: string
- **Response:**
  - `message`: Registration status
  - `cloud_token`: Token from the cloud API
  - `local_token`: Local API token
  - `user`: User data

### POST `/login/`

- **Description:** Obtain a local authentication token using username and password.
- **Request Body:**
  - `username`: string
  - `password`: string
- **Response:**
  - `token`: Local API token
  - `user_id`: User ID
  - `username`: Username

## Models

- **CustomUser**: Extends Django's `AbstractUser` and adds a `cloud_api_password` field to store the user's cloud API password for later use (e.g., for cloud API calls).

## Serializers

- **CustomUserRegistrationSerializer**: Handles user creation and ensures passwords are hashed.

## Management Commands

- **wait_for_db**: Custom Django management command that pauses execution until the database is available. Used in Docker entrypoints to ensure the DB is ready before running migrations or starting the server.

## Admin

- The `CustomUser` model is registered in the Django admin for user management.
