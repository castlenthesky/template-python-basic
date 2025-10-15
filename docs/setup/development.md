# Development Environment Setup

This guide walks you through setting up a local development environment for the Template Python Basic project.

![Development workspace](../assets/sunset.jpg)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://python.org)
- **uv** - Fast Python package manager - [Install uv](https://docs.astral.sh/uv/)
- **Git** - Version control - [Download Git](https://git-scm.com)
- **Database** - SQLite (included) or PostgreSQL for production

## Quick Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd template-python-basic
   ```

2. **Install dependencies with uv**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

4. **Run database migrations**
   ```bash
   uv run alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   uv run uvicorn src.api.server:app --reload --port 8000
   ```

## Environment Configuration

Your `.env` file should contain:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db
DATABASE_ECHO=false

# Application
APPLICATION_NAME=Template Python Basic
DEBUG=true
LOG_LEVEL=DEBUG

# Security (generate a secure key for production!)
SECRET_KEY=your-super-secret-development-key-here
```

> ⚠️ **Important**: Never commit your `.env` file to version control!

## Development Workflow

### Running Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_users.py
```

### Code Quality
```bash
# Format code
uv run black src/

# Lint code  
uv run ruff check src/

# Type checking
uv run mypy src/
```

### Database Operations
```bash
# Create new migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback migration
uv run alembic downgrade -1
```

## IDE Setup

### VS Code
Recommended extensions:
- Python
- Pylance
- Ruff
- SQLite Viewer

### PyCharm
1. Open the project folder
2. Configure Python interpreter to use the uv environment
3. Enable type checking and code formatting

## Troubleshooting

### Common Issues

**Import errors after adding dependencies**
```bash
# Refresh the virtual environment
uv sync
```

**Database connection errors**
```bash
# Recreate database
rm app.db
uv run alembic upgrade head
```

**Port already in use**
```bash
# Use a different port
uv run uvicorn src.api.server:app --reload --port 8001
```

## Development Tools

- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc  
- **Health Check**: http://localhost:8000/health
- **This Documentation**: http://localhost:8000/guide

## Next Steps

- [Configuration Guide](../configuration) - Detailed configuration options
- [API Guide](../api/index) - Explore the API endpoints
- [Database Setup](index) - Advanced database configuration

---

*Happy coding! 🚀*