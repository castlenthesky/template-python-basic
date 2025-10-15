# Health Check API

The health check API provides system status monitoring and diagnostics for the Template Python Basic application.

## Endpoint

**GET** `/health`

- **Authentication**: None required (public endpoint)
- **Rate Limiting**: Excluded from rate limits
- **Response Format**: JSON

## Response Structure

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123Z",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "response_time_ms": 15
  },
  "uptime_seconds": 3600
}
```

## Status Values

### Overall Status
- `healthy` - All systems operational
- `degraded` - Some non-critical issues detected
- `unhealthy` - Critical systems failing

### Database Status
- `connected` - Database is accessible and responding
- `slow` - Database responding but with high latency (>100ms)
- `disconnected` - Database connection failed

## Example Requests

### cURL
```bash
curl -X GET http://localhost:8000/health
```

### Python (requests)
```python
import requests

response = requests.get("http://localhost:8000/health")
health_data = response.json()
print(f"System status: {health_data['status']}")
```

### JavaScript (fetch)
```javascript
fetch('http://localhost:8000/health')
  .then(response => response.json())
  .then(data => console.log('Health status:', data.status));
```

## Monitoring Integration

This endpoint is designed for use with monitoring tools:

- **Uptime monitoring**: Check the endpoint returns 200 status
- **Performance monitoring**: Track database response times
- **Alerting**: Set up alerts for `unhealthy` or `degraded` status

## Response Codes

| Code | Description |
|------|-------------|
| 200  | System is healthy or degraded |
| 503  | System is unhealthy (service unavailable) |
| 500  | Internal error during health check |

## Related Resources

- [API Guide](index) - Full API documentation
- [Configuration](../configuration) - Health check configuration options
- [Setup Guide](../setup/index) - Application setup instructions

---

*The health endpoint is always available and requires no authentication for monitoring purposes.*