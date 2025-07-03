# Network App

This app manages networks, hosts, and ping monitoring for the monitoring backend. It provides endpoints for CRUD operations on networks and hosts, and background tasks for uptime monitoring and reporting.

## Endpoints

All endpoints are prefixed with `/api/v1/` in the main project.

### Network Endpoints

- **GET `/networks/`**
  - List all networks for the authenticated user (network admin).
- **POST `/networks/create/`**
  - Create a new network. Also creates the network in the cloud API.
- **GET `/networks/<pk>/`**
  - Retrieve details for a specific network.
- **PUT `/networks/<pk>/`**
  - Update a network. Also updates the network in the cloud API.
- **DELETE `/networks/<pk>/`**
  - Delete a network. Also deletes the network in the cloud API.

### Host Endpoints

- **GET `/hosts/`**
  - List all hosts for the authenticated user.
- **POST `/hosts/create/`**
  - Create a new host. Also creates the host in the cloud API.
- **GET `/hosts/<pk>/`**
  - Retrieve details for a specific host.
- **PUT `/hosts/<pk>/`**
  - Update a host. Also updates the host in the cloud API.
- **DELETE `/hosts/<pk>/`**
  - Delete a host. Also deletes the host in the cloud API.

## Models

- **Network**: Represents a network, linked to an admin user. Has a `cloud_pk` for cloud API sync.
- **Host**: Represents a host (device) in a network. Linked to a user and network. Has a `cloud_pk` for cloud API sync.
- **Ping**: Stores the result of a ping test for a host at a specific timestamp.

## Serializers

- **NetworkSerializer**: Serializes network data.
- **HostSerializer**: Serializes host data.

## Background Tasks (Celery)

- **ping_hosts**: Runs every 60 seconds. Pings all hosts and records their status in the `Ping` model.
- **submit_ping_data**: Runs every 5 minutes. Aggregates recent ping data and sends it to the cloud API's ingest endpoint.

## Utility Functions

- **get_cloud_token(user)**: Uses the user's stored cloud API password to obtain a fresh token from the cloud API for authenticated requests.

## Admin

- Networks, Hosts, and Pings are registered in the Django admin for management and inspection.
