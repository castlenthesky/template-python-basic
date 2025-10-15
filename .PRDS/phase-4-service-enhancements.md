# Phase 4: Service Layer Enhancements

## Problem Statement

The current service layer handles business logic well but lacks important cross-cutting concerns like input validation decorators, audit logging for sensitive operations, and caching mechanisms. This results in repetitive validation code and missed opportunities for performance optimization.

**Current Limitations:**
- Manual validation scattered throughout service methods
- No audit trail for sensitive business operations
- Missing caching strategies for expensive operations
- No standardized logging patterns for business events
- Limited observability into service-level performance

## Proposed Solution/Best Practice

Implement comprehensive service layer enhancements with:
1. **Validation Decorators**: Automated input validation with clear error messages
2. **Audit Logging**: Comprehensive audit trail for all business-critical operations
3. **Caching Layer**: Smart caching for expensive computations and queries
4. **Performance Monitoring**: Service-level metrics and observability
5. **Event Publishing**: Domain events for decoupled business logic

## Expected Enhancement

- **40% reduction** in repetitive validation code
- **Complete audit trail** for compliance and debugging
- **60% performance improvement** for cached operations
- **Enhanced observability** with structured business event logging

## Benefits Once Delivered

1. **Cleaner Services**: Validation logic separated from business logic
2. **Compliance Ready**: Complete audit trail for sensitive operations
3. **Better Performance**: Intelligent caching reduces database load
4. **Enhanced Monitoring**: Business-level metrics and insights
5. **Improved Maintainability**: Consistent patterns across all services

---

## Current Implementation Issues

### Problem: Manual Validation Throughout Services
```python
# src/services/users/service.py:32-36
async def create_user(self, session: AsyncSession, user_create: UserCreate) -> User:
    async def _create_user_operation(db_session: AsyncSession) -> User:
        if await self.username_exists(db_session, user_create.username):
            raise DuplicateError(f"Username '{user_create.username}' already exists")
        # ... more validation logic mixed with business logic
```

**Issues:**
- Validation logic mixed with business logic
- Repetitive validation patterns across services
- No standardized validation error handling
- Difficult to test validation logic in isolation

### Problem: No Audit Logging
```python  
# Current services have no audit trail
async def create_user(self, session: AsyncSession, user_create: UserCreate) -> User:
    user = await self._repository.create(db_session, user_create)
    logger.info(f"Successfully created user: {user_create.username}")  # Basic logging only
    return user
```

**Issues:**
- No structured audit events
- Missing sensitive operation tracking
- No compliance-ready audit trails
- Limited business event visibility

---

## Proposed Enhanced Implementation

### Solution: Validation Decorators
```python
# src/core/validation.py
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type
from pydantic import BaseModel, ValidationError as PydanticValidationError

class ValidationRule(BaseModel):
    """Base validation rule."""
    field: str
    message: str
    
    async def validate(self, value: Any, context: Dict[str, Any] = None) -> bool:
        raise NotImplementedError

class UniqueUsernameRule(ValidationRule):
    """Validate username uniqueness."""
    
    def __init__(self, repository_field: str = "_repository"):
        super().__init__(field="username", message="Username already exists")
        self.repository_field = repository_field
    
    async def validate(self, value: str, context: Dict[str, Any] = None) -> bool:
        if not context or "session" not in context or "service" not in context:
            return True
            
        service = context["service"]
        session = context["session"]
        repository = getattr(service, self.repository_field)
        
        return not await repository.username_exists(session, value)

def validate_input(*validation_rules: ValidationRule):
    """Decorator for validating service method inputs."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, session: AsyncSession, *args, **kwargs):
            # Extract validation context
            context = {
                "service": self,
                "session": session,
                "args": args,
                "kwargs": kwargs
            }
            
            # Get first argument (usually the input model)
            if args:
                input_model = args[0]
                
                # Validate each rule
                for rule in validation_rules:
                    if hasattr(input_model, rule.field):
                        field_value = getattr(input_model, rule.field)
                        is_valid = await rule.validate(field_value, context)
                        
                        if not is_valid:
                            raise ValidationError.for_field(
                                field=rule.field,
                                message=rule.message,
                                rejected_value=field_value
                            )
            
            return await func(self, session, *args, **kwargs)
        return wrapper
    return decorator
```

### Solution: Audit Logging System
```python
# src/core/audit.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

class AuditAction(Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"  
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ACCESS = "ACCESS"
    EXPORT = "EXPORT"

@dataclass
class AuditEvent:
    """Structured audit event."""
    id: UUID
    timestamp: datetime
    user_id: Optional[UUID]
    action: AuditAction
    resource_type: str
    resource_id: Optional[str]
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogger:
    """Centralized audit logging system."""
    
    def __init__(self):
        self.logger = logging.getLogger("audit")
    
    async def log_event(self, event: AuditEvent) -> None:
        """Log structured audit event."""
        # Log to structured logger
        self.logger.info(
            "Audit Event",
            extra={
                "audit_id": str(event.id),
                "timestamp": event.timestamp.isoformat(),
                "user_id": str(event.user_id) if event.user_id else None,
                "action": event.action.value,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "old_values": event.old_values,
                "new_values": event.new_values,
                "metadata": event.metadata,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent
            }
        )
        
        # Could also store in database table for compliance
        # await self._store_in_database(event)

def audit_operation(
    action: AuditAction,
    resource_type: str,
    include_old_values: bool = False,
    include_new_values: bool = True,
    sensitive: bool = False
):
    """Decorator for auditing service operations."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, session: AsyncSession, *args, **kwargs):
            audit_logger = AuditLogger()
            resource_id = None
            old_values = None
            
            # Capture old values for updates/deletes
            if include_old_values and action in [AuditAction.UPDATE, AuditAction.DELETE]:
                if args and hasattr(args[0], 'id'):
                    resource_id = str(args[0].id)
                    # Get existing resource for old values
                    existing = await self._repository.get(session, args[0].id)
                    if existing:
                        old_values = existing.model_dump()
            
            # Execute the operation
            result = await func(self, session, *args, **kwargs)
            
            # Capture new values
            new_values = None
            if include_new_values and result:
                if hasattr(result, 'model_dump'):
                    new_values = result.model_dump()
                    if not resource_id and hasattr(result, 'id'):
                        resource_id = str(result.id)
            
            # Create audit event
            event = AuditEvent(
                id=uuid4(),
                timestamp=datetime.utcnow(),
                user_id=None,  # TODO: Extract from context
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=old_values,
                new_values=new_values,
                metadata={
                    "function": func.__name__,
                    "service": self.__class__.__name__,
                    "sensitive": sensitive
                }
            )
            
            await audit_logger.log_event(event)
            return result
            
        return wrapper
    return decorator
```

### Solution: Service-Level Caching
```python
# src/core/caching.py
import asyncio
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional, Union
import hashlib

class CacheBackend:
    """Abstract cache backend."""
    
    async def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        raise NotImplementedError
    
    async def delete(self, key: str) -> None:
        raise NotImplementedError

class MemoryCache(CacheBackend):
    """Simple in-memory cache implementation."""
    
    def __init__(self):
        self._cache: Dict[str, tuple[Any, Optional[datetime]]] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key in self._cache:
                value, expires_at = self._cache[key]
                if expires_at is None or datetime.utcnow() < expires_at:
                    return value
                else:
                    del self._cache[key]
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        async with self._lock:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl) if ttl else None
            self._cache[key] = (value, expires_at)

# Global cache instance
cache = MemoryCache()

def cached(
    ttl: int = 300,  # 5 minutes default
    key_prefix: Optional[str] = None,
    vary_on: Optional[List[str]] = None
):
    """Decorator for caching service method results."""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Generate cache key
            cache_key_parts = [
                key_prefix or f"{self.__class__.__name__}.{func.__name__}",
            ]
            
            # Add method arguments to key
            if vary_on:
                for param in vary_on:
                    if param in kwargs:
                        cache_key_parts.append(f"{param}:{kwargs[param]}")
            else:
                # Use all serializable args/kwargs
                serializable_args = []
                for arg in args[1:]:  # Skip self
                    if hasattr(arg, 'model_dump'):
                        serializable_args.append(arg.model_dump())
                    elif isinstance(arg, (str, int, float, bool)):
                        serializable_args.append(arg)
                
                if serializable_args or kwargs:
                    data_hash = hashlib.md5(
                        json.dumps(
                            {"args": serializable_args, "kwargs": kwargs}, 
                            sort_keys=True, 
                            default=str
                        ).encode()
                    ).hexdigest()
                    cache_key_parts.append(data_hash[:8])
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = await func(self, *args, **kwargs)
            if result is not None:
                await cache.set(cache_key, result, ttl)
                logger.debug(f"Cached result for {cache_key}")
            
            return result
        return wrapper
    return decorator
```

---

## Impact on Other Modules

### Service Layer Transformation
```python
# BEFORE: Mixed validation and business logic
class UserService(TransactionalService):
    async def create_user(self, session: AsyncSession, user_create: UserCreate) -> User:
        async def _create_user_operation(db_session: AsyncSession) -> User:
            if await self.username_exists(db_session, user_create.username):
                raise DuplicateError(f"Username '{user_create.username}' already exists")
            
            user = await self._repository.create(db_session, user_create)
            logger.info(f"Successfully created user: {user_create.username}")
            return user

# AFTER: Clean, decorated service methods  
class UserService(TransactionalService):
    @validate_input(UniqueUsernameRule())
    @audit_operation(AuditAction.CREATE, "user", sensitive=True)
    async def create_user(self, session: AsyncSession, user_create: UserCreate) -> User:
        async def _create_user_operation(db_session: AsyncSession) -> User:
            # Pure business logic - validation handled by decorator
            user = await self._repository.create(db_session, user_create)
            return user
        
        return await self.execute_in_transaction(session, _create_user_operation)
    
    @cached(ttl=600, vary_on=["username"])  # Cache for 10 minutes
    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        """Get user by username with caching."""
        return await self._repository.get_by_username(session, username)
    
    @audit_operation(AuditAction.UPDATE, "user", include_old_values=True)
    @validate_input(UniqueUsernameRule())
    async def update_user(self, session: AsyncSession, user_id: UUID, user_update: UserUpdate) -> User:
        async def _update_user_operation(db_session: AsyncSession) -> User:
            user = await self._repository.get(db_session, user_id)
            if not user:
                raise NotFoundError(f"User with ID {user_id} not found")
            
            # Invalidate cache on update
            cache_key = f"UserService.get_by_username:username:{user.username}"
            await cache.delete(cache_key)
            
            return await self._repository.update(db_session, user, user_update)
        
        return await self.execute_in_transaction(session, _update_user_operation)
```

### Enhanced Business Logic Separation
```python
# AFTER: Repository with smart caching
class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    
    @cached(ttl=1800, key_prefix="user_task_counts")  # Cache expensive queries
    async def get_users_with_task_counts(
        self, session: AsyncSession, limit: int = 100
    ) -> List[Tuple[User, int]]:
        """Get users with their task counts - expensive query cached."""
        try:
            statement = select(User, func.count(Task.id)).outerjoin(Task).group_by(User.id).limit(limit)
            result = await session.execute(statement)
            results = result.all()
            logger.debug(f"Retrieved {len(results)} users with task counts")
            return [(user, count) for user, count in results]
        except Exception as e:
            logger.error(f"Error retrieving users with task counts: {e}")
            raise
```

### Structured Audit Trail Output
```json
// Audit log entry for user creation
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Audit Event",
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": null,
  "action": "CREATE", 
  "resource_type": "user",
  "resource_id": "123e4567-e89b-12d3-a456-426614174000",
  "old_values": null,
  "new_values": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "john_doe",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "metadata": {
    "function": "create_user",
    "service": "UserService",
    "sensitive": true
  }
}
```

### Performance Monitoring Integration
```python
# AFTER: Services with built-in metrics
from src.core.metrics import track_performance

class UserService(TransactionalService):
    
    @track_performance("user.create")
    @validate_input(UniqueUsernameRule())
    @audit_operation(AuditAction.CREATE, "user", sensitive=True)
    async def create_user(self, session: AsyncSession, user_create: UserCreate) -> User:
        # Business logic with automatic performance tracking
        pass
    
    @track_performance("user.search")
    @cached(ttl=300, vary_on=["search_term"])
    async def search_users(self, session: AsyncSession, search_term: str) -> List[User]:
        """Search users with performance tracking and caching."""
        filters = [QueryFilter("username", FilterOperator.LIKE, search_term)]
        return await self._repository.get_multi_advanced(session, filters=filters)
```

## Expected Output/Impact

1. **Cleaner Service Code**: Validation, caching, and audit logic separated from business logic
2. **Complete Audit Trail**: Every sensitive operation logged with structured data
3. **Significant Performance Gains**: 60% improvement for cached operations
4. **Enhanced Observability**: Business-level metrics and monitoring
5. **Improved Maintainability**: Consistent patterns and reusable decorators

**Quality Metrics:**
- Service method code reduced by 40% with decorator patterns
- Cache hit ratio of 80% for frequently accessed data
- Complete audit coverage for all sensitive operations
- Business metric visibility with automatic performance tracking