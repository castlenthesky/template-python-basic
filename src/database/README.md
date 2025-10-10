# Database Layer - Modern Async-First Architecture

This directory contains a production-ready, async-first database layer using SQLAlchemy, SQLModel, and async patterns following modern Python best practices for high-performance applications.

## 🏗️ Architecture Overview

```
src/database/              # ASYNC-FIRST DATABASE LAYER (Zero Business Logic)
├── __init__.py           # Clean async API exports
├── connection.py         # Async database connection & health utilities  
├── engine.py             # Async database engine configuration
├── models/               # SQLModel table definitions with async support
│   ├── __init__.py       # Model exports with mixins
│   ├── base.py           # Reusable model mixins (UUIDMixin, TimestampMixin)
│   ├── user.py           # User model & schemas
│   └── task.py           # Task model & schemas
├── repositories/         # Async data access layer (CRUD only)
│   ├── __init__.py       # Repository exports
│   ├── base.py           # Async base repository with common operations
│   ├── user.py           # User-specific async data queries
│   └── task.py           # Task-specific async data queries
└── migrations/           # Async Alembic migration management
    ├── env.py            # Async migration configuration
    └── versions/         # Migration version files

src/services/operations/  # Business logic layer (separate from database)
├── __init__.py          # Service exports
├── user_ops.py          # UserService with async business logic
└── task_ops.py          # TaskService with async business logic
```

## 🚀 Quick Start

### 1. Initialize the Database

```bash
# Generate a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations (runs async automatically)
alembic upgrade head

# View migration history
alembic history

# Downgrade to previous migration
alembic downgrade -1
```

## 📚 Usage Examples

### Basic Async Session Usage

```python
import asyncio
from src.database import get_async_db_connection
from src.database.repositories import UserRepository
from src.database.models import UserCreate

async def create_user_example():
    # Get async database connection
    async_db = get_async_db_connection()
    user_repo = UserRepository()
    
    async with async_db.create_session() as session:
        user_create = UserCreate(username="new_user")
        user = await user_repo.create(session, user_create)
        print(f"Created user: {user}")

# Run async function
asyncio.run(create_user_example())
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_db_connection
from src.database.repositories import UserRepository
from src.database.models import UserRead

app = FastAPI()
user_repo = UserRepository()
async_db = get_async_db_connection()

async def get_async_session():
    async with async_db.create_session() as session:
        yield session

@app.get("/users/", response_model=list[UserRead])
async def get_users(session: AsyncSession = Depends(get_async_session)):
    return await user_repo.get_multi(session, limit=10)

@app.post("/users/", response_model=UserRead)
async def create_user(
    user_data: UserCreate, 
    session: AsyncSession = Depends(get_async_session)
):
    return await user_repo.create(session, user_data)
```

### Repository Pattern Usage (Async Data Access)

```python
import asyncio
from src.database import get_async_db_connection
from src.database.repositories import UserRepository, TaskRepository
from src.database.models import TaskCreate, TaskStatus

async def repository_example():
    async_db = get_async_db_connection()
    user_repo = UserRepository()
    task_repo = TaskRepository()

    async with async_db.create_session() as session:
        # User operations
        user = await user_repo.get_by_username(session, "john_doe")
        username_exists = await user_repo.username_exists(session, "new_user")
        user_with_tasks = await user_repo.get_user_with_tasks(session, user.id)
        
        # Task creation
        task_create = TaskCreate(
            title="New task",
            description="Task description", 
            user_id=user.id
        )
        task = await task_repo.create(session, task_create)
        
        # Task queries
        user_tasks = await task_repo.get_by_user(session, user.id)
        completed_tasks = await task_repo.get_completed_tasks(session)
        pending_tasks = await task_repo.get_pending_tasks(session)
        search_results = await task_repo.search_by_title(session, "search term")
        
        # Bulk operations
        task_creates = [
            TaskCreate(title=f"Bulk task {i}", user_id=user.id)
            for i in range(5)
        ]
        bulk_tasks = await task_repo.bulk_create(session, task_creates)
        
        print(f"Created {len(bulk_tasks)} tasks")

# Run async function
asyncio.run(repository_example())
```

### Service Layer Usage (Business Logic)

```python
import asyncio
from src.database import get_async_db_connection
from src.services.operations import UserService, TaskService
from src.database.models import UserCreate, TaskCreate

async def service_example():
    async_db = get_async_db_connection()
    user_service = UserService()
    task_service = TaskService()

    async with async_db.create_session() as session:
        # Business logic operations
        user = await user_service.create_user(session, UserCreate(username="john_doe"))
        
        task_create = TaskCreate(
            title="New task",
            description="Task description", 
            user_id=user.id
        )
        task = await task_service.create(session, task_create)
        
        # Business operations with validation
        completed_task = await task_service.mark_completed(session, task.id)

asyncio.run(service_example())
```

## 🔧 Async Database Configuration

Database configuration uses a single `DATABASE_URL` environment variable with async drivers:

```bash
# Production Databases (Async)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
DATABASE_URL=mysql+aiomysql://user:password@host:3306/dbname  

# Development & Testing (Async)
DATABASE_URL=sqlite+aiosqlite:///data/app.db
DATABASE_URL=sqlite+aiosqlite:///:memory:  # In-memory for tests

# Connection Pool Settings (Optional)
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
SQL_ECHO=false  # Enable for development debugging
```

## 🗃️ Models & Mixins

### Base Model Mixins
- **`BaseModel`**: Common Pydantic configuration for all models
- **`UUIDMixin`**: Adds UUID primary key field
- **`TimestampMixin`**: Adds `created_at` and `updated_at` timestamp fields

### User Model
- **Table**: `users`
- **Fields**: `id` (UUID), `username` (unique), `created_at`, `updated_at`
- **Relationships**: One-to-many with tasks
- **Schemas**: `UserCreate`, `UserRead`, `UserUpdate`

### Task Model  
- **Table**: `tasks`
- **Fields**: `id` (UUID), `title`, `description`, `status`, `user_id`, `created_at`, `updated_at`, `completed_at`
- **Relationships**: Many-to-one with user
- **Schemas**: `TaskCreate`, `TaskRead`, `TaskUpdate`
- **Status Enum**: `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`

## 🏛️ Data Access Layer

### UserRepository (Async Data Access)
- `get(session, user_id)` - Get user by ID
- `get_multi(session, skip, limit, filters)` - Get multiple users with pagination
- `create(session, user_create)` - Create user record
- `update(session, user, user_update)` - Update user record
- `delete(session, user_id)` - Delete user record
- `get_by_username(session, username)` - Find user by username
- `username_exists(session, username)` - Check username availability
- `get_user_with_tasks(session, user_id)` - Get user with tasks loaded
- `get_users_with_task_counts(session, limit)` - Get users with task counts

### TaskRepository (Async Data Access)
- `get(session, task_id)` - Get task by ID
- `get_multi(session, skip, limit, filters)` - Get multiple tasks with pagination
- `create(session, task_create)` - Create task record
- `update(session, task, task_update)` - Update task record
- `delete(session, task_id)` - Delete task record
- `get_by_user(session, user_id)` - Get all user tasks
- `get_by_status(session, status)` - Filter by status
- `get_completed_tasks(session)` - Get completed tasks
- `get_pending_tasks(session)` - Get pending tasks
- `get_in_progress_tasks(session)` - Get in-progress tasks
- `search_by_title(session, search_term)` - Search by title
- `get_user_tasks_by_status(session, user_id, status)` - Get user tasks by status

### BaseRepository (Async Generic CRUD)
- `get(session, id)` - Get single record by ID
- `get_multi(session, skip, limit, filters)` - Get multiple records with pagination
- `create(session, obj_in)` - Create new record
- `update(session, db_obj, obj_in)` - Update existing record
- `delete(session, id)` - Delete record by ID
- `count(session, filters)` - Count records with optional filters
- `exists(session, id)` - Check if record exists by ID
- `bulk_create(session, objs_in)` - Bulk create multiple records
- `bulk_update(session, updates)` - Bulk update multiple records
- `bulk_delete(session, ids)` - Bulk delete multiple records

## 🎯 Modern Best Practices

### ✅ **Async-First Architecture**
- **High Performance**: Native async support for maximum concurrency
- **Modern Databases**: Works with PostgreSQL, MySQL, SQLite (all async)
- **Migration Excellence**: Alembic with async SQLAlchemy integration
- **Production Ready**: Optimized connection pooling and error handling

### ✅ **Clean Architecture**
- **Zero Business Logic**: Database layer contains ONLY database concerns
- **Clear Separation**: Business logic moved to `src/services/` layer
- **Single Responsibility**: Each file has one clear purpose
- **Conventional Structure**: Follows Django-inspired patterns

### ✅ **Advanced Async Session Management**
- **Async Sessions**: High-performance asynchronous session support
- **Dependency Injection**: FastAPI-native async session management
- **Context Managers**: Automatic commit/rollback handling
- **Connection Health**: Built-in async health checks
- **Proper Cleanup**: Automatic resource management and disposal

### ✅ **Model Design**
- **SQLModel**: Type safety and Pydantic integration
- **Reusable Mixins**: `UUIDMixin`, `TimestampMixin` for common functionality
- **Separate CRUD Schemas**: Create/Read/Update for different operations
- **Proper Relationships**: Foreign keys with cascade behavior
- **Enum Types**: Type-safe status fields

### ✅ **Async Repository Pattern**
- **Pure Data Access**: No business logic in repositories
- **Generic Base Class**: Common async CRUD operations with type safety
- **Specialized Methods**: Model-specific async queries and operations
- **Consistent Error Handling**: Proper exception handling and logging
- **Bulk Operations**: Efficient async batch processing capabilities
- **Native Async**: All operations optimized for async performance

### ✅ **Modern Database Support**
- **Async Databases**: PostgreSQL (+asyncpg), MySQL (+aiomysql), SQLite (+aiosqlite)
- **Production Ready**: Optimized for high-concurrency applications
- **Connection Pooling**: Advanced pooling strategies per database type
- **Health Monitoring**: Comprehensive async connection health checks
- **Type Safety**: Full validation of async database configuration

### ✅ **Async Migration Management**
- **Alembic Integration**: Async schema version control
- **Auto-generation**: Migrations from model changes  
- **Forward/Backward**: Compatible async migration paths
- **Environment Aware**: Optimized configs for async databases

### ✅ **Error Handling & Logging**
- **Comprehensive Logging**: Debug info for all operations
- **Transaction Safety**: Rollback on errors
- **Meaningful Messages**: Clear error descriptions
- **Graceful Degradation**: Proper cleanup on failures

### ✅ **Development Experience**
- **Type Safety**: Full async type hints with SQLModel
- **IDE Support**: Autocomplete and error detection for async code
- **Documentation**: Comprehensive async examples and API docs
- **Testing Ready**: Easy to mock and test async operations

## 📁 Architecture Principles

### **Database Layer** (`src/database/`)
- **Models**: Table definitions and schema validation with mixins
- **Repositories**: Pure async data access operations (CRUD)
- **Connection**: Advanced async connection management
- **Engines**: Async engine creation and caching
- **Migrations**: Async Alembic configuration

### **Service Layer** (`src/services/`)
- **Business Logic**: Async validation, workflows, complex operations
- **Service Classes**: Orchestrate multiple async repositories
- **Domain Rules**: Application-specific constraints and logic
- **Native Async**: Full async support throughout

### **Supported Databases**

| Database | Connection String | Use Case |
|----------|-------------------|----------|
| **PostgreSQL** | `postgresql+asyncpg://user:pass@host/db` | Production apps, web services |
| **MySQL** | `mysql+aiomysql://user:pass@host/db` | Web applications, e-commerce |
| **SQLite** | `sqlite+aiosqlite:///data/app.db` | Development, testing |

### **Migration Strategy**
Simplified async-first migration system:
- **Async migrations** for all supported databases
- **Automatic detection** of async database configuration
- **Single command** works across all database types: `alembic upgrade head`

### **Architecture Benefits**
1. **High Performance**: Native async support for maximum concurrency
2. **Simplicity**: Single async pattern eliminates complexity
3. **Testability**: Easy to unit test async operations
4. **Maintainability**: Clear boundaries with consistent async patterns
5. **Scalability**: Built for high-concurrency applications
6. **Team Development**: Consistent async patterns across layers
7. **Future-Proof**: Modern async-first foundation

This architecture provides an **async-first foundation** for modern Python applications requiring high-performance, scalable, and maintainable database functionality optimized for contemporary web applications.