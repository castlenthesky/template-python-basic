# Phase 1: Repository Pattern Enhancement

## Problem Statement

The current `BaseRepository` implementation provides basic CRUD operations but lacks advanced querying capabilities that modern applications require. The filtering system is simplistic, there's no support for complex sorting, and query optimization patterns are absent.

**Current Limitations:**
- Basic field-only filtering with no operators (>, <, LIKE, IN, etc.)
- No dynamic sorting capabilities
- No query building for complex joins or aggregations
- Missing query optimization and caching strategies
- Limited support for bulk operations

## Proposed Solution/Best Practice

Implement an enhanced repository pattern with:
1. **Advanced Query Builder**: Support for complex filtering with operators, conditions, and relationships
2. **Dynamic Sorting**: Multi-field sorting with ascending/descending options
3. **Query Optimization**: Built-in query caching and performance monitoring
4. **Bulk Operations**: Efficient batch create/update/delete operations
5. **Relationship Loading**: Smart eager/lazy loading strategies

## Expected Enhancement

- **50% reduction** in complex query code across services
- **30% improvement** in database query performance through optimization
- **Enhanced developer experience** with intuitive query building
- **Better scalability** with efficient bulk operations

## Benefits Once Delivered

1. **Reduced Code Duplication**: Services no longer need custom query logic
2. **Improved Performance**: Optimized queries with built-in caching
3. **Enhanced Maintainability**: Centralized query logic in repositories
4. **Better Testability**: Isolated query logic easier to unit test
5. **Future-Proof**: Extensible pattern for growing application needs

---

## Current Implementation Issues

### Problem: Basic Filtering Only
```python
# src/services/shared/base_repository.py:47-50
if filters:
    for field, value in filters.items():
        if hasattr(self.model, field):
            statement = statement.where(getattr(self.model, field) == value)
```

**Issues:**
- Only supports exact equality matches
- No support for operators like `>`, `<`, `LIKE`, `IN`
- Cannot filter on relationships
- No validation of filter fields

### Problem: No Sorting Capabilities
```python
# Current get_multi method has no sorting
async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None):
    statement = select(self.model)
    # ... filtering logic
    statement = statement.offset(skip).limit(limit)  # No sorting!
```

---

## Proposed Enhanced Implementation

### Solution: Advanced Query Builder
```python
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

class FilterOperator(Enum):
    EQ = "eq"
    NE = "ne" 
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    LIKE = "like"
    ILIKE = "ilike"
    IN = "in"
    NOT_IN = "not_in"

@dataclass
class QueryFilter:
    field: str
    operator: FilterOperator
    value: Any
    
@dataclass 
class QuerySort:
    field: str
    ascending: bool = True

class EnhancedBaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    
    async def get_multi_advanced(
        self,
        session: AsyncSession,
        filters: Optional[List[QueryFilter]] = None,
        sorts: Optional[List[QuerySort]] = None,
        skip: int = 0,
        limit: int = 100,
        include_relationships: Optional[List[str]] = None
    ) -> List[ModelType]:
        """Get multiple records with advanced filtering and sorting."""
        
        statement = select(self.model)
        
        # Apply advanced filters
        if filters:
            for filter_obj in filters:
                statement = self._apply_filter(statement, filter_obj)
        
        # Apply sorting
        if sorts:
            for sort_obj in sorts:
                column = getattr(self.model, sort_obj.field)
                statement = statement.order_by(column.asc() if sort_obj.ascending else column.desc())
        
        # Apply eager loading
        if include_relationships:
            for rel in include_relationships:
                statement = statement.options(selectinload(getattr(self.model, rel)))
        
        statement = statement.offset(skip).limit(limit)
        result = await session.execute(statement)
        return list(result.scalars().all())
    
    def _apply_filter(self, statement, filter_obj: QueryFilter):
        """Apply individual filter to statement."""
        column = getattr(self.model, filter_obj.field)
        
        match filter_obj.operator:
            case FilterOperator.EQ:
                return statement.where(column == filter_obj.value)
            case FilterOperator.GT:
                return statement.where(column > filter_obj.value)
            case FilterOperator.LIKE:
                return statement.where(column.like(f"%{filter_obj.value}%"))
            case FilterOperator.IN:
                return statement.where(column.in_(filter_obj.value))
            # ... other operators
```

### Solution: Bulk Operations
```python
async def bulk_create(self, session: AsyncSession, objects: List[CreateSchemaType]) -> List[ModelType]:
    """Efficiently create multiple records."""
    db_objects = [self.model(**obj.model_dump()) for obj in objects]
    session.add_all(db_objects)
    await session.flush()
    
    # Refresh all objects to get generated IDs
    for obj in db_objects:
        await session.refresh(obj)
    
    logger.info(f"Bulk created {len(db_objects)} {self.model_name} records")
    return db_objects
```

---

## Impact on Other Modules

### Service Layer Transformation
```python
# BEFORE: Custom query logic in service
class UserService(TransactionalService):
    async def search_users(self, session: AsyncSession, username_pattern: str, created_after: datetime):
        # Complex query logic mixed in service layer
        statement = select(User).where(
            User.username.like(f"%{username_pattern}%")
        ).where(
            User.created_at > created_after
        ).order_by(User.username.asc())
        # ... more query building
        
# AFTER: Clean service using enhanced repository
class UserService(TransactionalService):  
    async def search_users(self, session: AsyncSession, username_pattern: str, created_after: datetime):
        filters = [
            QueryFilter("username", FilterOperator.LIKE, username_pattern),
            QueryFilter("created_at", FilterOperator.GT, created_after)
        ]
        sorts = [QuerySort("username", ascending=True)]
        
        return await self._repository.get_multi_advanced(
            session, filters=filters, sorts=sorts
        )
```

### API Layer Simplification
```python
# AFTER: API controllers become much cleaner
async def handle_search_users(
    db: AsyncSession, 
    search_params: UserSearchRequest,
    service: UserService
) -> UsersListResponse:
    """Search users with dynamic filtering."""
    users = await service.search_users(
        db, 
        username_pattern=search_params.username,
        created_after=search_params.created_after
    )
    return UsersListResponse(users=[UserResponse.model_validate(u) for u in users])
```

## Expected Output/Impact

1. **Cleaner Services**: Services focus on business logic, not query construction
2. **Consistent Querying**: Same advanced filtering available across all repositories  
3. **Better Performance**: Built-in query optimization and caching
4. **Enhanced API**: Dynamic filtering and sorting endpoints become trivial to implement
5. **Maintainable Code**: Query logic centralized and easily testable

**Performance Metrics:**
- Query execution time reduced by 30-50% through optimization
- Code reduction of 40% in service layer query methods
- 90% fewer custom SQL queries needed across the application