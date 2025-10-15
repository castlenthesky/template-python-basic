# Phase 5: Performance & Testing Infrastructure

## Problem Statement

The current application lacks comprehensive performance monitoring, advanced testing infrastructure, and background task processing capabilities. Without these foundational pieces, it's difficult to identify performance bottlenecks, ensure code quality at scale, and handle long-running operations efficiently.

**Current Limitations:**
- No database query performance monitoring
- Basic test infrastructure without factory patterns
- Missing background task processing for long operations
- Limited test coverage for edge cases and complex scenarios
- No performance benchmarking or regression detection

## Proposed Solution/Best Practice

Implement comprehensive performance and testing infrastructure with:
1. **Database Performance Monitoring**: Query analysis and optimization tools
2. **Enhanced Test Infrastructure**: Factory patterns, fixtures, and property-based testing
3. **Background Task Processing**: Async job queue for long-running operations
4. **Performance Benchmarking**: Automated performance regression detection
5. **Advanced Testing Patterns**: Integration tests, load testing, and chaos engineering

## Expected Enhancement

- **Real-time visibility** into database performance and query optimization
- **50% faster test development** with factory patterns and fixtures
- **Scalable architecture** with background task processing
- **Quality assurance** with comprehensive test coverage and performance monitoring

## Benefits Once Delivered

1. **Proactive Performance Management**: Early detection of performance regressions
2. **Faster Development Cycles**: Efficient testing infrastructure
3. **Scalable Operations**: Background processing for heavy workloads
4. **Quality Assurance**: Comprehensive test coverage and reliability
5. **Production Readiness**: Monitoring and observability for production systems

---

## Current Implementation Issues

### Problem: No Query Performance Monitoring
```python
# Current repository methods have no performance tracking
async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100):
    statement = select(self.model)
    # ... query logic
    result = await session.execute(statement)  # No timing or analysis
    return list(result.scalars().all())
```

**Issues:**
- No visibility into slow queries
- Missing query execution time tracking
- No automatic query optimization suggestions
- Cannot identify N+1 query problems

### Problem: Basic Test Infrastructure
```python
# tests/conftest.py - Basic test setup only
@pytest.fixture
async def db_session():
    # Simple session fixture
    pass

# Manual test data creation
def test_create_user():
    user_data = UserCreate(username="testuser")  # Manual creation
    # ... test logic
```

**Issues:**
- Manual test data creation is repetitive
- No factory patterns for complex object graphs
- Limited test data variety and edge cases
- Difficult to maintain test fixtures

---

## Proposed Enhanced Implementation

### Solution: Database Performance Monitoring
```python
# src/core/db_monitoring.py
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import asyncio
import logging

@dataclass
class QueryMetrics:
    """Query performance metrics."""
    query: str
    execution_time: float
    row_count: Optional[int]
    timestamp: datetime
    slow_query: bool
    table_names: List[str]
    operation_type: str  # SELECT, INSERT, UPDATE, DELETE

class QueryMonitor:
    """Database query performance monitor."""
    
    def __init__(self, slow_query_threshold: float = 1.0):
        self.slow_query_threshold = slow_query_threshold
        self.metrics: List[QueryMetrics] = []
        self.logger = logging.getLogger("db.performance")
    
    @asynccontextmanager
    async def monitor_query(self, query: str):
        """Monitor query execution time and log metrics."""
        start_time = time.time()
        row_count = None
        
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            is_slow = execution_time > self.slow_query_threshold
            
            # Extract table names and operation type
            table_names = self._extract_table_names(query)
            operation_type = self._extract_operation_type(query)
            
            metrics = QueryMetrics(
                query=query,
                execution_time=execution_time,
                row_count=row_count,
                timestamp=datetime.utcnow(),
                slow_query=is_slow,
                table_names=table_names,
                operation_type=operation_type
            )
            
            self.metrics.append(metrics)
            
            # Log slow queries
            if is_slow:
                self.logger.warning(
                    f"Slow query detected ({execution_time:.3f}s): {query[:100]}...",
                    extra={
                        "execution_time": execution_time,
                        "query": query,
                        "tables": table_names,
                        "operation": operation_type
                    }
                )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        if not self.metrics:
            return {"total_queries": 0}
        
        total_queries = len(self.metrics)
        slow_queries = sum(1 for m in self.metrics if m.slow_query)
        avg_execution_time = sum(m.execution_time for m in self.metrics) / total_queries
        
        # Group by operation type
        operations = {}
        for metric in self.metrics:
            op = metric.operation_type
            if op not in operations:
                operations[op] = {"count": 0, "total_time": 0, "slow_count": 0}
            operations[op]["count"] += 1
            operations[op]["total_time"] += metric.execution_time
            if metric.slow_query:
                operations[op]["slow_count"] += 1
        
        return {
            "total_queries": total_queries,
            "slow_queries": slow_queries,
            "slow_query_percentage": (slow_queries / total_queries) * 100,
            "average_execution_time": avg_execution_time,
            "operations": operations,
            "most_frequent_tables": self._get_table_frequency()
        }

# Enhanced repository with monitoring
class MonitoredBaseRepository(BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
    
    def __init__(self, model: Type[ModelType]):
        super().__init__(model)
        self.query_monitor = QueryMonitor()
    
    async def get_multi(self, session: AsyncSession, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> List[ModelType]:
        """Get multiple records with performance monitoring."""
        statement = select(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
        
        statement = statement.offset(skip).limit(limit)
        query_str = str(statement)
        
        async with self.query_monitor.monitor_query(query_str):
            result = await session.execute(statement)
            results = list(result.scalars().all())
        
        logger.debug(f"Retrieved {len(results)} {self.model_name} records")
        return results
```

### Solution: Advanced Test Infrastructure
```python
# tests/factories.py
import factory
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Any, Dict

from src.database.models.public.user import User, UserCreate
from src.database.models.public.task import Task, TaskCreate

class UserFactory(factory.Factory):
    """Factory for creating User test instances."""
    
    class Meta:
        model = UserCreate
    
    username = factory.Sequence(lambda n: f"user{n}")
    
    @classmethod
    def create_batch_with_tasks(cls, size: int = 5, tasks_per_user: int = 3) -> List[User]:
        """Create batch of users with associated tasks."""
        users = []
        for i in range(size):
            user = cls()
            tasks = TaskFactory.create_batch(tasks_per_user, user_id=user.id)
            user.tasks = tasks
            users.append(user)
        return users

class TaskFactory(factory.Factory):
    """Factory for creating Task test instances."""
    
    class Meta:
        model = TaskCreate
    
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=200)
    completed = factory.Faker('boolean', chance_of_getting_true=25)
    user_id = factory.LazyFunction(uuid4)
    
    @factory.post_generation
    def set_completion_date(obj, create, extracted, **kwargs):
        """Set completion date for completed tasks."""
        if obj.completed:
            obj.completed_at = factory.Faker('date_time_between', 
                                           start_date='-30d', 
                                           end_date='now').generate()

# tests/fixtures/database.py
@pytest.fixture
async def db_session_with_data():
    """Database session with pre-populated test data."""
    async with get_test_session() as session:
        # Create test users with tasks
        users = UserFactory.create_batch_with_tasks(size=10, tasks_per_user=5)
        
        for user_data in users:
            user = User(**user_data.model_dump())
            session.add(user)
        
        await session.commit()
        yield session

@pytest.fixture  
def performance_tracker():
    """Fixture for tracking test performance."""
    tracker = QueryMonitor(slow_query_threshold=0.1)  # Stricter for tests
    yield tracker
    
    # Report after test
    report = tracker.get_performance_report()
    if report["slow_queries"] > 0:
        pytest.warnings.warn(
            f"Test generated {report['slow_queries']} slow queries",
            category=UserWarning
        )
```

### Solution: Background Task Processing
```python
# src/core/background_jobs.py
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4
import pickle
import logging

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class Job:
    """Background job definition."""
    id: UUID
    name: str
    function: str
    args: tuple
    kwargs: dict
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 0

class JobQueue:
    """Async background job queue."""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.jobs: Dict[UUID, Job] = {}
        self.pending_queue: asyncio.Queue = asyncio.Queue()
        self.workers: List[asyncio.Task] = []
        self.running = False
        self.logger = logging.getLogger("background_jobs")
        
        # Registry of available job functions
        self.job_registry: Dict[str, Callable] = {}
    
    def register_job_handler(self, name: str, handler: Callable):
        """Register a job handler function."""
        self.job_registry[name] = handler
    
    async def enqueue(
        self, 
        function_name: str, 
        *args,
        job_name: Optional[str] = None,
        priority: int = 0,
        max_retries: int = 3,
        **kwargs
    ) -> UUID:
        """Enqueue a background job."""
        job_id = uuid4()
        
        job = Job(
            id=job_id,
            name=job_name or function_name,
            function=function_name,
            args=args,
            kwargs=kwargs,
            status=JobStatus.PENDING,
            created_at=datetime.utcnow(),
            priority=priority,
            max_retries=max_retries
        )
        
        self.jobs[job_id] = job
        await self.pending_queue.put(job)
        
        self.logger.info(f"Enqueued job {job_name or function_name} ({job_id})")
        return job_id
    
    async def start_workers(self):
        """Start background workers."""
        self.running = True
        
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(f"worker-{i}"))
            self.workers.append(worker)
        
        self.logger.info(f"Started {self.max_workers} background workers")
    
    async def _worker(self, worker_name: str):
        """Background worker to process jobs."""
        while self.running:
            try:
                # Get job with timeout
                job = await asyncio.wait_for(self.pending_queue.get(), timeout=1.0)
                
                if job.function not in self.job_registry:
                    job.status = JobStatus.FAILED
                    job.error = f"Unknown job function: {job.function}"
                    continue
                
                # Execute job
                await self._execute_job(job, worker_name)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Worker {worker_name} error: {e}")
    
    async def _execute_job(self, job: Job, worker_name: str):
        """Execute a single job."""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        
        try:
            handler = self.job_registry[job.function]
            self.logger.info(f"Worker {worker_name} executing job {job.name} ({job.id})")
            
            result = await handler(*job.args, **job.kwargs)
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.result = result
            
            self.logger.info(f"Job {job.name} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Job {job.name} failed: {e}")
            
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.status = JobStatus.RETRYING
                # Re-queue with delay
                await asyncio.sleep(2 ** job.retry_count)  # Exponential backoff
                await self.pending_queue.put(job)
            else:
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.completed_at = datetime.utcnow()

# Global job queue
job_queue = JobQueue()

# Example job handlers
async def send_welcome_email(user_id: UUID, email: str):
    """Background job to send welcome email."""
    # Simulate email sending
    await asyncio.sleep(2)
    logger.info(f"Welcome email sent to {email}")
    return {"status": "sent", "recipient": email}

async def generate_user_report(user_id: UUID, report_type: str):
    """Background job to generate user reports."""
    # Simulate report generation
    await asyncio.sleep(5)
    return {"report_url": f"/reports/{user_id}/{report_type}.pdf"}

# Register job handlers
job_queue.register_job_handler("send_welcome_email", send_welcome_email)
job_queue.register_job_handler("generate_user_report", generate_user_report)
```

---

## Impact on Other Modules

### Service Layer with Background Jobs
```python
# AFTER: Services can offload heavy work to background jobs
class UserService(TransactionalService):
    
    @audit_operation(AuditAction.CREATE, "user", sensitive=True) 
    async def create_user(self, session: AsyncSession, user_create: UserCreate) -> User:
        """Create user and trigger background welcome processes."""
        user = await self._repository.create(session, user_create)
        
        # Enqueue background jobs
        await job_queue.enqueue(
            "send_welcome_email",
            user.id,
            user.email,
            job_name=f"welcome_email_{user.username}"
        )
        
        await job_queue.enqueue(
            "generate_user_report", 
            user.id,
            "onboarding",
            job_name=f"onboarding_report_{user.username}",
            priority=1
        )
        
        return user
```

### Enhanced Test Scenarios
```python
# AFTER: Comprehensive test patterns
class TestUserService:
    
    @pytest.mark.asyncio
    async def test_create_user_batch_performance(self, db_session_with_data, performance_tracker):
        """Test batch user creation performance."""
        service = UserService(UserRepository())
        
        # Create batch of users
        user_data_batch = UserFactory.create_batch(100)
        
        start_time = time.time()
        for user_data in user_data_batch:
            await service.create_user(db_session_with_data, user_data)
        execution_time = time.time() - start_time
        
        # Performance assertions
        assert execution_time < 5.0, f"Batch creation took {execution_time}s (max: 5s)"
        
        # Check for N+1 queries
        report = performance_tracker.get_performance_report()
        assert report["slow_queries"] == 0, f"Found {report['slow_queries']} slow queries"
    
    @pytest.mark.property
    def test_username_validation_property(self):
        """Property-based test for username validation."""
        
        @given(st.text(min_size=1, max_size=100))
        def test_username_accepts_valid_chars(username):
            # Test that usernames with valid characters are accepted
            if re.match(r'^[a-zA-Z0-9_]{3,50}$', username):
                user_data = UserCreate(username=username)
                assert user_data.username == username
        
        test_username_accepts_valid_chars()
    
    @pytest.mark.asyncio
    async def test_concurrent_user_creation(self, db_session):
        """Test concurrent user creation doesn't cause race conditions."""
        service = UserService(UserRepository())
        
        # Create multiple users concurrently
        tasks = [
            service.create_user(db_session, UserFactory(username=f"concurrent_user_{i}"))
            for i in range(10)
        ]
        
        users = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all users were created successfully
        successful_creates = [u for u in users if isinstance(u, User)]
        assert len(successful_creates) == 10
```

### Performance Dashboard Integration
```python
# AFTER: API endpoints for performance monitoring
@app.get("/admin/performance/database")
async def get_database_performance():
    """Get database performance metrics."""
    # Collect metrics from all repositories
    all_metrics = []
    for repo_class in [UserRepository, TaskRepository]:
        repo = repo_class()
        if hasattr(repo, 'query_monitor'):
            metrics = repo.query_monitor.get_performance_report()
            metrics['repository'] = repo_class.__name__
            all_metrics.append(metrics)
    
    return {"database_performance": all_metrics}

@app.get("/admin/jobs/status")
async def get_job_queue_status():
    """Get background job queue status."""
    pending_jobs = [j for j in job_queue.jobs.values() if j.status == JobStatus.PENDING]
    running_jobs = [j for j in job_queue.jobs.values() if j.status == JobStatus.RUNNING]
    failed_jobs = [j for j in job_queue.jobs.values() if j.status == JobStatus.FAILED]
    
    return {
        "queue_status": {
            "pending": len(pending_jobs),
            "running": len(running_jobs), 
            "failed": len(failed_jobs),
            "workers": len(job_queue.workers)
        }
    }
```

## Expected Output/Impact

1. **Proactive Performance Management**: Real-time query monitoring and optimization
2. **Accelerated Development**: Factory patterns reduce test setup time by 50%
3. **Scalable Architecture**: Background processing handles heavy workloads
4. **Quality Assurance**: Comprehensive test coverage with property-based testing
5. **Production-Ready Monitoring**: Complete observability into system performance

**Performance Metrics:**
- Query performance visibility with automatic slow query detection
- Test development speed increased by 50% with factory patterns
- Background job processing capacity for long-running operations
- Performance regression detection with automated benchmarking
- 95% test coverage with edge case and property-based testing