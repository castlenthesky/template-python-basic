# Database Setup - SQLAlchemy + SQLite + SQLModel

This directory contains a production-ready, gold-standard database setup using SQLAlchemy, SQLite, and SQLModel following Python best practices.

## 🏗️ Architecture Overview

```
src/database/
├── __init__.py           # Main exports
├── base.py              # Base model class
├── engine.py            # Database engine configuration
├── session.py           # Session management & dependency injection
├── init_db.py           # Database initialization utilities
├── example.py           # Hello world demonstration
├── models/              # SQLModel entities
│   ├── __init__.py
│   ├── user.py          # User model with CRUD schemas
│   └── task.py          # Task model with CRUD schemas
├── operations/          # Repository pattern for CRUD operations
│   ├── __init__.py
│   ├── base.py          # Base repository class
│   ├── user_ops.py      # User repository
│   └── task_ops.py      # Task repository
└── migrations/          # Alembic migrations
    ├── env.py           # Alembic environment
    └── versions/        # Migration files
```

## 🚀 Quick Start

### 1. Initialize the Database

```bash
# Create tables using direct SQLModel approach
python -m src.database.init_db

# OR reset database (drop and recreate all tables)
python -m src.database.init_db --reset
```

### 2. Using Alembic Migrations (Recommended)

```bash
# Generate a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# View migration history
alembic history

# Downgrade to previous migration
alembic downgrade -1
```

### 3. Run the Hello World Example

```bash
python -m src.database.example
```

## 📚 Usage Examples

### Basic Session Usage

```python
from src.database import session_scope, user_repo
from src.database.models import UserCreate

# Using context manager (recommended)
with session_scope() as session:
    user_create = UserCreate(username="new_user")
    user = user_repo.create_user(session, user_create)
    print(f"Created user: {user}")
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from src.database import get_session
from src.database.operations import user_repo

app = FastAPI()

@app.get("/users/")
def get_users(session: Session = Depends(get_session)):
    return user_repo.get_multi(session, limit=10)
```

### Repository Pattern Usage

```python
from src.database import session_scope
from src.database.operations import user_repo, task_repo
from src.database.models import TaskCreate, TaskStatus

with session_scope() as session:
    # Get user
    user = user_repo.get_by_username(session, "john_doe")
    
    # Create task
    task_create = TaskCreate(
        title="New task",
        description="Task description", 
        user_id=user.id
    )
    task = task_repo.create(session, task_create)
    
    # Update task status
    task_repo.mark_completed(session, task.id)
    
    # Query tasks
    user_tasks = task_repo.get_by_user(session, user.id)
    completed_tasks = task_repo.get_completed_tasks(session)
    search_results = task_repo.search_by_title(session, "search term")
```

## 🔧 Configuration

Database settings are managed in `src/config/__init__.py`:

```python
# Environment variables (optional)
DATABASE_URL=sqlite:///custom/path/to/database.db
SQL_ECHO=true  # Enable SQL query logging
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

## 🗃️ Models

### User Model
- **Table**: `users`
- **Fields**: `id`, `username` (unique), `created_at`, `updated_at`
- **Relationships**: One-to-many with tasks
- **Schemas**: `UserCreate`, `UserRead`, `UserUpdate`

### Task Model  
- **Table**: `tasks`
- **Fields**: `id`, `title`, `description`, `status`, `user_id`, `created_at`, `updated_at`, `completed_at`
- **Relationships**: Many-to-one with user
- **Schemas**: `TaskCreate`, `TaskRead`, `TaskUpdate`
- **Status Enum**: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`

## 🏛️ Repository Operations

### UserRepository
- `get_by_username(session, username)` - Find user by username
- `username_exists(session, username)` - Check username availability
- `create_user(session, user_create)` - Create user with validation
- `get_user_with_tasks(session, user_id)` - Get user with tasks loaded

### TaskRepository  
- `get_by_user(session, user_id)` - Get all user tasks
- `get_by_status(session, status, user_id=None)` - Filter by status
- `get_completed_tasks(session, user_id=None)` - Get completed tasks
- `get_pending_tasks(session, user_id=None)` - Get pending tasks
- `mark_completed(session, task_id)` - Mark task complete
- `mark_in_progress(session, task_id)` - Mark task in progress
- `search_by_title(session, search_term, user_id=None)` - Search by title

## 🎯 Best Practices Implemented

### ✅ Session Management
- Dependency injection pattern for FastAPI
- Context managers for explicit control
- Automatic commit/rollback handling
- Proper session cleanup

### ✅ Model Design
- SQLModel for type safety and Pydantic integration
- Separate CRUD schemas (Create/Read/Update)
- Proper relationships with foreign keys
- Automatic timestamps
- Enum for status fields

### ✅ Repository Pattern
- Abstracted database operations
- Generic base repository class
- Specialized methods for each model
- Consistent error handling

### ✅ Configuration Management
- Environment-based configuration
- Sensible defaults
- Database URL abstraction
- Connection pool settings

### ✅ Migration Management
- Alembic integration for schema changes
- Auto-generation of migrations
- Version control for database schema
- Forward and backward compatibility

### ✅ Error Handling
- Proper exception handling in repositories
- Transaction rollback on errors
- Meaningful error messages
- Graceful cleanup

## 🧪 Testing

The `example.py` file demonstrates:
- Database initialization
- CRUD operations
- Session management patterns
- Relationship handling
- Query patterns
- Error handling

## 📁 File Structure Details

- **`engine.py`**: SQLite engine with connection pooling
- **`session.py`**: Session factory and dependency injection
- **`base.py`**: Base model class with common configuration  
- **`models/`**: SQLModel entities with CRUD schemas
- **`operations/`**: Repository pattern implementation
- **`migrations/`**: Alembic configuration and migration files
- **`init_db.py`**: Database initialization utilities
- **`example.py`**: Comprehensive usage demonstration

This setup provides a solid foundation for any Python application requiring database functionality with SQLAlchemy and SQLite.