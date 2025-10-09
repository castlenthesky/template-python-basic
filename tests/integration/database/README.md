# Database Integration Tests

This directory contains comprehensive integration tests for the database layer, covering all aspects of the SQLAlchemy + SQLite + SQLModel setup.

## 🧪 Test Structure

### Test Files Overview

- **`test_user_repository.py`** - User repository CRUD operations
- **`test_task_repository.py`** - Task repository CRUD operations  
- **`test_session_management.py`** - Session handling patterns
- **`test_alembic_migrations.py`** - Migration system tests

### Shared Test Infrastructure

The tests use shared fixtures from `tests/fixtures/database.py`:

- **`test_db_engine`** - Session-scoped SQLite engine
- **`test_db_manager`** - Database manager with helper methods
- **`test_session`** - Function-scoped session with automatic rollback
- **`test_user`** - Single test user fixture
- **`test_task`** - Single test task fixture
- **`test_dataset`** - Comprehensive multi-user/task dataset

## 🔧 Running the Tests

### Run All Database Integration Tests
```bash
pytest tests/integration/database/ -v
```

### Run Specific Test Files
```bash
# User repository tests
pytest tests/integration/database/test_user_repository.py -v

# Task repository tests
pytest tests/integration/database/test_task_repository.py -v

# Session management tests
pytest tests/integration/database/test_session_management.py -v

# Migration tests
pytest tests/integration/database/test_alembic_migrations.py -v
```

### Run Specific Test Classes
```bash
pytest tests/integration/database/test_user_repository.py::TestUserRepository -v
```

### Run With Coverage
```bash
pytest tests/integration/database/ --cov=src.database --cov-report=html
```

## 📋 Test Coverage

### User Repository Tests (`test_user_repository.py`)

✅ **CRUD Operations**
- Create user with validation
- Get user by ID and username
- Update user information
- Delete user
- Handle duplicate usernames

✅ **Query Operations**
- Multiple users with pagination
- Username existence checks
- User counting

✅ **Edge Cases**
- Non-existent users
- Invalid operations

### Task Repository Tests (`test_task_repository.py`)

✅ **CRUD Operations**
- Create task with relationships
- Get task by ID
- Update task fields
- Delete task with cascade

✅ **Query Operations**
- Tasks by user
- Tasks by status
- Search by title
- Pagination support
- Task counting

✅ **Status Management**
- Mark tasks completed
- Mark tasks in progress
- Status filtering
- Completion timestamps

✅ **Relationships**
- Task-user relationships
- Foreign key constraints

### Session Management Tests (`test_session_management.py`)

✅ **Context Managers**
- `session_scope()` success flows
- Automatic rollback on exceptions
- Transaction boundaries

✅ **Dependency Injection**
- `get_session()` for FastAPI
- Exception handling
- Session cleanup

✅ **Concurrency & Isolation**
- Multiple concurrent sessions
- Transaction isolation
- Proper commit/rollback

✅ **Complex Operations**
- Nested operations in single session
- Multi-table transactions
- Error recovery

### Migration Tests (`test_alembic_migrations.py`)

✅ **Migration Operations**
- Upgrade to latest version
- Downgrade to base
- Migration history tracking
- Idempotency

✅ **Schema Validation**
- Table creation
- Column definitions
- Foreign keys
- Indexes
- Data types

✅ **Model Compatibility**
- Schema matches models
- Migration completeness
- Data insertion validation

## 🎯 Key Testing Patterns

### 1. Isolated Test Data
Each test uses fresh, isolated data with automatic cleanup:

```python
def test_user_creation(test_session: Session, sample_user_data):
    user_create = UserCreate(**sample_user_data)
    user = user_repo.create_user(test_session, user_create)
    assert user.username == sample_user_data["username"]
```

### 2. Comprehensive Dataset Testing
Use the `test_dataset` fixture for complex scenarios:

```python
def test_complex_queries(test_session: Session, test_dataset):
    alice = test_dataset["users"]["alice"]
    alice_tasks = task_repo.get_by_user(test_session, alice.id)
    assert len(alice_tasks) == 2
```

### 3. Error Condition Testing
Verify proper error handling:

```python
def test_duplicate_username_fails(test_session: Session, sample_user_data):
    user_create = UserCreate(**sample_user_data)
    user_repo.create_user(test_session, user_create)
    
    with pytest.raises(ValueError, match="already exists"):
        user_repo.create_user(test_session, user_create)
```

### 4. Relationship Testing
Validate model relationships:

```python
def test_task_user_relationship(test_session: Session, test_user: User):
    task = create_test_task(test_session, user_id=test_user.id)
    found_task = task_repo.get(test_session, task.id)
    assert found_task.user.username == test_user.username
```

## 🛠️ Test Database Management

### Automatic Setup
- Each test gets a fresh SQLite database
- All tables are created automatically
- Sessions are isolated with automatic rollback

### Cleanup Strategy
- Test database files are automatically removed
- No persistent test data between runs
- Memory usage is controlled

### Performance Optimization
- Session-scoped engine creation
- Function-scoped session isolation
- Minimal database I/O

## 🎨 Writing New Tests

### Adding User Repository Tests
```python
def test_new_user_feature(test_session: Session, test_db_manager):
    # Arrange
    user = test_db_manager.create_test_user(test_session, username="new_test")
    
    # Act
    result = user_repo.new_feature(test_session, user.id)
    
    # Assert
    assert result is not None
```

### Adding Task Repository Tests
```python
def test_new_task_feature(test_session: Session, test_task: Task):
    # Act
    result = task_repo.new_feature(test_session, test_task.id)
    
    # Assert
    assert result.status == TaskStatus.EXPECTED
```

### Testing Error Conditions
```python
def test_edge_case_handling(test_session: Session):
    with pytest.raises(ExpectedError, match="expected message"):
        repository.operation_that_should_fail(test_session, invalid_data)
```

## 🚀 Best Practices

### ✅ Do's
- Use provided fixtures for consistency
- Test both success and failure paths
- Verify database state after operations
- Use descriptive test names
- Group related tests in classes
- Test edge cases and error conditions

### ❌ Don'ts
- Don't create persistent test data
- Don't skip session cleanup
- Don't ignore transaction boundaries
- Don't hardcode IDs or data
- Don't skip error condition testing

### 🎯 Focus Areas
- **Data Integrity** - Verify constraints work
- **Relationship Consistency** - Test foreign keys
- **Transaction Safety** - Ensure proper rollbacks
- **Performance** - Keep tests fast and isolated
- **Error Handling** - Test failure scenarios

## 📊 Running Performance Tests

For performance-focused testing:

```bash
# Run with timing information
pytest tests/integration/database/ -v --durations=10

# Run with profiling
pytest tests/integration/database/ --profile

# Memory usage monitoring
pytest tests/integration/database/ --memray
```

This comprehensive test suite ensures the database layer is robust, reliable, and ready for production use.