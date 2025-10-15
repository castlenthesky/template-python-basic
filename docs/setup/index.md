# Configuration

This project uses environment variables for configuration. All settings can be configured via the `.env` file.

## Environment Variables

### Database Settings
```env
DATABASE_URL=sqlite+aiosqlite:///./app.db
DATABASE_ECHO=false
```

### Application Settings
```env
APPLICATION_NAME=Template Python Basic
APPLICATION_DESCRIPTION=A basic Python template with FastAPI
APPLICATION_VERSION=1.0.0
```

### Security Settings
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Development Settings
```env
DEBUG=true
LOG_LEVEL=INFO
```

## Configuration Classes

The application uses Pydantic settings for type-safe configuration management:

```python
from src.config import settings

# Access configuration values
print(settings.DATABASE_URL)
print(settings.APPLICATION_NAME)
```

## Environment-Specific Configs

### Development
- Enable debug mode
- Use SQLite database
- Verbose logging

### Production
- Disable debug mode  
- Use PostgreSQL database
- Error-level logging only

## Validation

All configuration values are validated at startup. Invalid configurations will prevent the application from starting with clear error messages.