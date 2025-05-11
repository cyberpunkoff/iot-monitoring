# IoT Monitoring API Service

API service for retrieving sensor data from ClickHouse database. This service provides endpoints to access current sensor readings, historical data, and aggregated statistics. Includes user authentication and device management.

## Features

- User authentication with JWT tokens
- Role-based access control (USER and ADMIN roles)
- Device management (create, read, update, delete)
- Get current sensor readings
- Get historical sensor data
- Get aggregated statistics (min, max, avg) for a time period

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables (copy `.env.example` to `.env` and update values)
   - Don't forget to set a secure `JWT_SECRET_KEY` in production!

3. Run the service:
   ```
   uvicorn app.main:app --reload
   ```

## Authentication

- Register: `POST /auth/register` - Create a new user account
- Login: `POST /auth/token` - Get a JWT token for authentication
- Current User: `GET /auth/me` - Get information about the authenticated user

All data endpoints require authentication with a valid JWT token.

## Role-Based Access

- Regular users (USER role) can access sensor data and metadata
- Admin users (ADMIN role) can manage devices (create, update, delete)

## Device Management

- Create device: `POST /devices` - Create a new device (admin only)
- List devices: `GET /devices` - Get a list of all devices
- Get device: `GET /devices/{device_id}` - Get details for a specific device
- Update device: `PUT /devices/{device_id}` - Update a device (admin only)
- Delete device: `DELETE /devices/{device_id}` - Delete a device (admin only)

## API Documentation

Once the service is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Admin User

A default admin user is created automatically with the following credentials:
- Username: `admin`
- Password: `admin123`

Please change these credentials in production! 