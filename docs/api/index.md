# API Guide

This document provides detailed information about the available API endpoints.

## Authentication

All endpoints (except health checks) require authentication via JWT tokens.

### Headers
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

## Endpoints

### Health Check
- **GET** `/health`
- Returns the current status of the application

### Users
- **GET** `/users` - List all users
- **POST** `/users` - Create a new user
- **GET** `/users/{id}` - Get user by ID
- **PUT** `/users/{id}` - Update user
- **DELETE** `/users/{id}` - Delete user

### Tasks
- **GET** `/tasks` - List all tasks
- **POST** `/tasks` - Create a new task
- **GET** `/tasks/{id}` - Get task by ID
- **PUT** `/tasks/{id}` - Update task
- **DELETE** `/tasks/{id}` - Delete task

## Error Handling

The API returns standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request |
| 401  | Unauthorized |
| 404  | Not Found |
| 500  | Internal Server Error |

## Rate Limiting

API requests are limited to 100 requests per minute per IP address.