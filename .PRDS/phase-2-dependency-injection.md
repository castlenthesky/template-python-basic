# Phase 2: Dependency Injection Improvements

## Problem Statement

The current dependency injection system in `src/api/dependencies.py` has repetitive code patterns, lacks proper interface abstractions, and creates tightly coupled dependencies. This makes testing difficult and reduces code maintainability.

**Current Issues:**
- Repetitive dependency creation functions
- Direct class instantiation instead of interface-based design  
- Hard to mock dependencies for testing
- No centralized dependency configuration
- Tight coupling between layers

## Proposed Solution/Best Practice

Implement a robust dependency injection system with:
1. **Interface Abstractions**: Define protocols/interfaces for all services and repositories
2. **Dependency Container**: Centralized container for managing object lifecycles
3. **Factory Patterns**: Clean factory methods for complex dependency trees
4. **Configuration-Based**: External configuration for dependency bindings
5. **Testing Support**: Easy mock injection for unit tests

## Expected Enhancement

- **60% reduction** in boilerplate dependency code
- **Improved testability** with easy mock injection
- **Better separation** between interface and implementation
- **Centralized configuration** of all application dependencies

## Benefits Once Delivered

1. **Enhanced Testability**: Easy to inject mocks and test doubles
2. **Reduced Coupling**: Services depend on interfaces, not concrete classes
3. **Improved Maintainability**: Centralized dependency management
4. **Better Scalability**: Easy to swap implementations and add new services
5. **Cleaner Code**: Reduced boilerplate in dependency creation

---

## Current Implementation Issues

### Problem: Repetitive Dependency Functions
```python
# src/api/dependencies.py:25-47
def get_user_repository() -> UserRepository:
    """Dependency to provide user repository."""
    return UserRepository()

def get_user_service() -> UserService:
    """Dependency to provide user service with repository dependency."""
    return UserService(get_user_repository())

def get_task_repository() -> TaskRepository:
    """Dependency to provide task repository."""
    return TaskRepository()

def get_task_service() -> TaskService:
    """Dependency to provide task service with repository dependency."""
    return TaskService(get_task_repository())

def get_health_service() -> HealthService:
    """Dependency to provide health service."""
    return HealthService()
```

**Issues:**
- Repetitive patterns for each service/repository pair
- Hard-coded dependencies making testing difficult
- No lifecycle management (always creates new instances)

### Problem: No Interface Abstractions
```python
# Services directly depend on concrete classes
class UserService(TransactionalService):
    def __init__(self, repository: UserRepository):  # Concrete class!
        self._repository = repository
```

**Issues:**  
- Tight coupling to specific implementations
- Cannot easily swap implementations
- Difficult to create test doubles

---

## Proposed Enhanced Implementation

### Solution: Interface Abstractions
```python
# src/services/shared/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol
from uuid import UUID

class IUserRepository(Protocol):
    """Interface for user repository operations."""
    
    async def get(self, session: AsyncSession, id: UUID) -> Optional[User]:
        ...
    
    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        ...
    
    async def create(self, session: AsyncSession, obj_in: UserCreate) -> User:
        ...
    
    async def get_multi_advanced(
        self, 
        session: AsyncSession, 
        filters: Optional[List[QueryFilter]] = None,
        sorts: Optional[List[QuerySort]] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        ...

class IUserService(Protocol):
    """Interface for user service operations."""
    
    async def create_user(self, session: AsyncSession, user_create: UserCreate) -> User:
        ...
    
    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        ...
    
    async def search_users(self, session: AsyncSession, **kwargs) -> List[User]:
        ...
```

### Solution: Dependency Container
```python
# src/core/container.py
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Type, TypeVar
from enum import Enum

class Lifetime(Enum):
    TRANSIENT = "transient"  # New instance every time
    SINGLETON = "singleton"  # Single instance for app lifetime
    SCOPED = "scoped"       # Single instance per request

T = TypeVar('T')

@dataclass
class ServiceDescriptor:
    service_type: Type
    implementation_type: Type
    lifetime: Lifetime
    factory: Optional[Callable[..., Any]] = None
    instance: Optional[Any] = field(default=None, init=False)

class DependencyContainer:
    """Centralized dependency injection container."""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_transient(self, service_type: Type[T], implementation_type: Type[T]) -> 'DependencyContainer':
        """Register a transient service (new instance each time)."""
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type, 
            lifetime=Lifetime.TRANSIENT
        )
        return self
    
    def register_singleton(self, service_type: Type[T], implementation_type: Type[T]) -> 'DependencyContainer':
        """Register a singleton service (single instance)."""
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=implementation_type,
            lifetime=Lifetime.SINGLETON
        )
        return self
    
    def register_factory(self, service_type: Type[T], factory: Callable[..., T], lifetime: Lifetime = Lifetime.TRANSIENT) -> 'DependencyContainer':
        """Register a service with custom factory function."""
        self._services[service_type] = ServiceDescriptor(
            service_type=service_type,
            implementation_type=service_type,
            lifetime=lifetime,
            factory=factory
        )
        return self
    
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance."""
        if service_type not in self._services:
            raise ValueError(f"Service {service_type} not registered")
        
        descriptor = self._services[service_type]
        
        # Handle singleton lifetime
        if descriptor.lifetime == Lifetime.SINGLETON:
            if service_type not in self._singletons:
                self._singletons[service_type] = self._create_instance(descriptor)
            return self._singletons[service_type]
        
        # Handle transient lifetime
        return self._create_instance(descriptor)
    
    def _create_instance(self, descriptor: ServiceDescriptor):
        """Create service instance using factory or constructor."""
        if descriptor.factory:
            return descriptor.factory(self)
        
        # Auto-resolve constructor dependencies
        return self._auto_resolve_constructor(descriptor.implementation_type)
    
    def _auto_resolve_constructor(self, implementation_type: Type):
        """Auto-resolve constructor dependencies using type hints."""
        import inspect
        sig = inspect.signature(implementation_type.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            if param.annotation != inspect.Parameter.empty:
                kwargs[param_name] = self.resolve(param.annotation)
        
        return implementation_type(**kwargs)
```

### Solution: Clean Service Configuration  
```python
# src/core/service_config.py
from src.core.container import DependencyContainer
from src.services.shared.interfaces import IUserRepository, IUserService, ITaskRepository, ITaskService
from src.services.users.repository import UserRepository  
from src.services.users.service import UserService
from src.services.tasks.repository import TaskRepository
from src.services.tasks.service import TaskService

def configure_services() -> DependencyContainer:
    """Configure all application services and dependencies."""
    container = DependencyContainer()
    
    # Register repositories
    container.register_transient(IUserRepository, UserRepository)
    container.register_transient(ITaskRepository, TaskRepository)
    
    # Register services with auto-resolved dependencies
    container.register_transient(IUserService, UserService)  
    container.register_transient(ITaskService, TaskService)
    
    # Register singleton services
    container.register_singleton(IHealthService, HealthService)
    
    return container

# Global container instance
container = configure_services()
```

---

## Impact on Other Modules

### Service Layer Transformation
```python
# BEFORE: Concrete dependencies
class UserService(TransactionalService):
    def __init__(self, repository: UserRepository):  # Concrete!
        self._repository = repository

# AFTER: Interface-based dependencies  
class UserService(TransactionalService):
    def __init__(self, repository: IUserRepository):  # Interface!
        self._repository = repository
```

### API Dependencies Simplification
```python
# BEFORE: Repetitive dependency functions
# src/api/dependencies.py - 20+ lines of repetitive code

# AFTER: Clean container-based resolution
from src.core.service_config import container
from src.services.shared.interfaces import IUserService, ITaskService

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide async database session."""
    db_connection = get_async_db_connection()
    session = db_connection.create_session()
    try:
        yield session
    finally:
        await session.close()

def get_user_service() -> IUserService:
    """Get user service from container."""
    return container.resolve(IUserService)

def get_task_service() -> ITaskService:
    """Get task service from container."""
    return container.resolve(ITaskService)
```

### Enhanced Testing Capabilities
```python
# BEFORE: Difficult to mock dependencies
def test_create_user():
    # Had to mock concrete classes
    with patch('src.services.users.repository.UserRepository') as mock_repo:
        # Complex mocking setup...

# AFTER: Easy interface mocking
def test_create_user():
    # Create test container with mocks
    test_container = DependencyContainer()
    mock_user_repo = Mock(spec=IUserRepository)
    
    test_container.register_factory(IUserRepository, lambda c: mock_user_repo)
    test_container.register_transient(IUserService, UserService)
    
    user_service = test_container.resolve(IUserService)
    # Clean, easy testing!
```

### Router Layer Benefits
```python
# AFTER: Routers remain unchanged but get enhanced testability
@users_router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db_session),
    service: IUserService = Depends(get_user_service)  # Interface type!
) -> UserResponse:
    """Create a new user."""
    return await handle_create_user(db, user_data, service)
```

## Expected Output/Impact

1. **Reduced Boilerplate**: 60% less code in dependency management
2. **Enhanced Testability**: Easy mock injection and test isolation  
3. **Improved Flexibility**: Swap implementations without code changes
4. **Better Maintainability**: Centralized dependency configuration
5. **Cleaner Architecture**: Clear separation between interfaces and implementations

**Code Quality Metrics:**
- Dependency injection code reduced from 47 lines to ~10 lines
- Test setup time reduced by 70% with easy mocking
- Zero coupling between service interfaces and implementations
- Single configuration point for all application dependencies