# API Reference Guide

This document provides comprehensive information about all available API endpoints in the Template Python Basic application.

> 💡 **Quick Start**: New to the API? Check out our [Getting Started Guide](../getting-started) first!

## Base URL

All API endpoints are available at: `http://localhost:8000`

## Authentication

Most endpoints require authentication via JWT tokens. Health endpoints are publicly accessible.

### Headers
```http
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

## Core Endpoints

### Health Check
- **GET** `/health` - System health and status
- **Response**: Health metrics and database connectivity
- **Public**: No authentication required

### Users Management
- **GET** `/users` - List all users (paginated)
- **POST** `/users` - Create a new user
- **GET** `/users/{id}` - Get user by ID
- **GET** `/users/{id}/with-tasks` - Get user with their tasks
- **PUT** `/users/{id}` - Update user information
- **DELETE** `/users/{id}` - Delete user account

### Tasks Management
- **GET** `/tasks` - List all tasks (paginated)
- **POST** `/tasks` - Create a new task
- **GET** `/tasks/{id}` - Get task by ID
- **PUT** `/tasks/{id}` - Update task details
- **DELETE** `/tasks/{id}` - Delete task

### Documentation
- **GET** `/guide/` - This documentation system
- **GET** `/guide/{path}` - Navigate documentation pages
- **GET** `/guide/assets/{file}` - Static assets (images, etc.)

## Response Format

All API responses follow a consistent JSON structure:

```json
{
  "data": { /* actual response data */ },
  "message": "Success",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Error Handling

The API returns standard HTTP status codes with descriptive error messages:

| Code | Description | Example |
|------|-------------|---------|
| 200  | Success | Request completed successfully |
| 400  | Bad Request | Invalid input parameters |
| 401  | Unauthorized | Missing or invalid authentication |
| 404  | Not Found | Resource does not exist |
| 422  | Validation Error | Request body validation failed |
| 500  | Internal Server Error | Unexpected server error |

## Rate Limiting

- **Rate**: 100 requests per minute per IP address
- **Headers**: Rate limit info included in response headers
- **Exceeded**: Returns `429 Too Many Requests`

## Interactive Documentation

- **Swagger UI**: Available at `/docs` - Interactive API explorer
- **ReDoc**: Available at `/redoc` - Alternative API documentation

## Related Resources

- [Configuration Guide](../configuration) - API configuration options
- [Setup Instructions](../setup/index) - Database and environment setup
- [Home](../index) - Return to documentation home

---

*For live, interactive API testing, visit the [Swagger UI](/docs) endpoint.*