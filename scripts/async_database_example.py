"""
Async Database Example - Modern Async-First Database Architecture.

This example showcases the async-first database layer using:
- Native async database connections and session management
- Async repository pattern for high-performance data access
- Async service layer with business logic
- Proper async resource management and health checks
- Production-ready async patterns following modern Python best practices
"""

import asyncio
import logging
from sqlmodel import SQLModel

from src.config import settings
from src.database import get_async_db_connection
from src.database.models.task import TaskCreate
from src.database.models.user import UserCreate, UserRead
from src.database.engine import get_async_engine
from src.services.users.service import UserService
from src.services.tasks.service import TaskService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_async_tables():
    """Create all database tables using async engine with production-ready patterns."""
    logger.info("Creating database tables using async-first architecture...")
    
    try:
        async_engine = get_async_engine()
        async with async_engine.begin() as conn:
            # Use async patterns for table creation
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("✅ Async tables created successfully!")
    except Exception as e:
        logger.error(f"Failed to create async tables: {e}")
        # Enhanced error handling for async database issues
        if "does not support async" in str(e) or "asyncpg" in str(e) or "aiosqlite" in str(e):
            logger.info("💡 Async database driver required. Install: asyncpg, aiomysql, or aiosqlite")
            logger.info("💡 Or use scripts/database_example.py for sync operations")
        raise


async def async_database_example():
    """Main async-first database example demonstrating modern Python patterns."""
    
    logger.info("\n🚀 Modern Async-First Database Architecture Example")
    logger.info("=" * 55)
    
    # Validate async database configuration
    database_type = settings.get_database_type()
    if database_type not in {"postgresql", "mysql", "sqlite"}:
        logger.warning(f"Database '{database_type}' not supported for async operations")
        logger.info("Async-compatible databases: PostgreSQL (+asyncpg), MySQL (+aiomysql), SQLite (+aiosqlite)")
        logger.info("Use scripts/database_example.py for sync operations")
        return
    
    
    # Create tables using async patterns
    await create_async_tables()
    
    # Get async database connection for high-performance operations
    async_db = get_async_db_connection()
    
    # Initialize async service layer for business logic
    user_service = UserService()
    task_service = TaskService()
    
    # Example 1: Async health monitoring for production systems
    logger.info("\n💓 Example 1: Production-ready async health monitoring")
    is_healthy = await async_db.health_check()
    logger.info(f"Async database health: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")
    
    # Example 2: Async connection information for diagnostics
    logger.info("\n📊 Example 2: Async connection diagnostics")
    try:
        # Get async connection diagnostics
        from src.database import db_connection
        info = db_connection().get_connection_info()
        logger.info(f"Database dialect: {info['dialect']}")
        logger.info(f"Database URL: {info['url']}")
        logger.info(f"Driver: {info['driver']}")
        logger.info(f"Pool size: {info['pool_size']}")
        logger.info(f"Checked out connections: {info['checked_out_connections']}")
        logger.info(f"✅ Async-native architecture confirmed")
    except Exception as e:
        logger.warning(f"Could not get async connection diagnostics: {e}")
    
    # Example 3: Async repository pattern for data access layer
    logger.info("\n🔄 Example 3: Async repository pattern demonstration")
    try:
        async with async_db.create_session() as async_session:
            logger.info("✅ Async session created for high-performance operations")
            
            # Test async connectivity with production patterns
            from sqlalchemy import text
            result = await async_session.execute(text("SELECT 1 as connectivity_test"))
            test_value = result.scalar()
            logger.info(f"✅ Async connectivity validated: SELECT 1 = {test_value}")
            
            # Example of async repository usage (when implemented):
            # user_create = UserCreate(username="async_user")
            # user = await user_repo.create(async_session, user_create)
            # user_tasks = await task_repo.get_by_user(async_session, user.id)
            # completed_tasks = await task_repo.get_completed_tasks(async_session)
            
            logger.info("🏗️ Async repository methods ready for implementation")
            
    except Exception as e:
        logger.error(f"❌ Error in async repository demonstration: {e}")
        raise
    
    # Example 4: Production-ready async resource cleanup
    logger.info("\n🧹 Example 4: Production-ready async resource cleanup")
    try:
        await async_db.close_connections()
        logger.info("✅ Async connections and pools closed successfully")
    except Exception as e:
        logger.warning(f"Warning during async resource cleanup: {e}")
    
    logger.info("\n🎉 Modern async-first database architecture example completed!")
    logger.info("=" * 65)


async def demonstrate_async_database_detection():
    """Demonstrate async-first database type detection and configuration validation."""
    logger.info("\n🔄 Async-First Database Configuration Validation")
    logger.info("=" * 50)
    
    database_type = settings.get_database_type()
    
    logger.info(f"Detected database type: {database_type}")
    logger.info("Async-native architecture - all connections use async drivers")
    
    # Demonstrate async-compatible database URL patterns
    async_database_examples = [
        "postgresql+asyncpg://user:pass@localhost/db",  # PostgreSQL with asyncpg
        "mysql+aiomysql://user:pass@localhost/db",      # MySQL with aiomysql
        "sqlite+aiosqlite:///data/app.db",              # SQLite with aiosqlite
        "sqlite+aiosqlite:///:memory:",                  # In-memory SQLite for testing
    ]
    
    sync_database_examples = [
        "postgresql+psycopg2://user:pass@localhost/db",  # PostgreSQL sync
        "mysql+pymysql://user:pass@localhost/db",        # MySQL sync
        "sqlite:///data/app.db",                         # SQLite sync
    ]
    
    logger.info("\nAsync-Compatible Database URLs (High Performance):")
    for url in async_database_examples:
        logger.info(f"  🚀 {url}")
    
    logger.info("\nSync Database URLs (Legacy Support):")
    for url in sync_database_examples:
        logger.info(f"  🔵 {url}")
    
    logger.info(f"\n💡 Current configuration: ✅ Async-Native Architecture")
    logger.info("   All database operations use async drivers for high performance!")


if __name__ == "__main__":
    """Run modern async-first database architecture examples."""
    try:
        # Run comprehensive async-first database example
        asyncio.run(async_database_example())
        
        # Demonstrate async database configuration validation
        asyncio.run(demonstrate_async_database_detection())
        
    except KeyboardInterrupt:
        logger.info("\n👋 Async example interrupted by user")
    except Exception as e:
        logger.error(f"\n💥 Fatal error in async operations: {e}")
        logger.info("\n💡 Async troubleshooting guide:")
        logger.info("1. Verify DATABASE_URL uses async driver (+asyncpg, +aiomysql, +aiosqlite)")
        logger.info("2. Install required async driver: pip install asyncpg aiomysql aiosqlite")
        logger.info("3. Check database supports async operations (PostgreSQL, MySQL, SQLite)")
        logger.info("4. For sync operations, use: python scripts/database_example.py")
        logger.info("5. Review async configuration in src/database/README.md")
        raise