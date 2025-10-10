"""Modern async-native database initialization utilities.

Production-ready async-first database initialization following modern Python patterns
and async-first database architecture principles.
"""

import asyncio
from sqlmodel import SQLModel

from src.config import settings
from src.database.engine import get_async_engine
from src.database.models.task import Task
from src.database.models.user import User


async def create_tables():
    """Create all database tables using async-native patterns."""
    print("Creating database tables with async-native architecture...")

    # Import models to ensure they're registered with SQLModel metadata  
    _ = User, Task

    # Create all tables using async engine for high-performance operations
    async_engine = get_async_engine()
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    print("✅ Database tables created successfully!")


async def drop_tables():
    """Drop all database tables using async-native patterns (use with caution!)."""
    print("Dropping all database tables with async-native architecture...")

    # Import models to ensure they're registered with SQLModel metadata
    _ = User, Task

    # Drop all tables using async engine
    async_engine = get_async_engine()
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    print("✅ Database tables dropped successfully!")


async def reset_database():
    """Reset database using async-native architecture."""
    print("Resetting database with async-native architecture...")
    await drop_tables()
    await create_tables()
    print("✅ Database reset completed!")


async def validate_async_configuration():
    """Validate that the database is properly configured for async operations."""
    print("\n🔍 Validating async database configuration...")
    
    database_type = settings.get_database_type()
    print(f"Database type: {database_type}")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    # Use the existing validation method from settings
    try:
        settings.validate_async_database()
        print("✅ Async database configuration validated!")
    except ValueError as e:
        raise ValueError(
            f"Database configuration error: {e}\n"
            f"Please update to use async drivers:\n"
            f"  - PostgreSQL: +asyncpg (postgresql+asyncpg://...)\n"
            f"  - MySQL: +aiomysql (mysql+aiomysql://...)\n"
            f"  - SQLite: +aiosqlite (sqlite+aiosqlite://...)"
        )
    
    if database_type not in {"postgresql", "mysql", "sqlite"}:
        raise ValueError(
            f"Database type '{database_type}' not supported for async operations.\n"
            f"Supported async databases: PostgreSQL, MySQL, SQLite"
        )


async def main():
    """Main async function for database initialization."""
    import sys
    
    try:
        # Always validate async configuration first
        await validate_async_configuration()
        
        if len(sys.argv) > 1:
            if sys.argv[1] == "--reset":
                print("🔄 Database reset requested...")
                await reset_database()
            elif sys.argv[1] == "--drop":
                print("🗑️  Database drop requested...")
                await drop_tables()
            elif sys.argv[1] == "--create":
                print("🏗️  Database creation requested...")
                await create_tables()
            else:
                print("❌ Unknown option. Available options:")
                print("  --create : Create database tables")
                print("  --drop   : Drop database tables")
                print("  --reset  : Drop and recreate database tables")
                sys.exit(1)
        else:
            print("🏗️  Creating database tables...")
            await create_tables()
            
    except Exception as e:
        print(f"\n💥 Fatal error during async database initialization: {e}")
        print("\n💡 Async troubleshooting guide:")
        print("1. Verify DATABASE_URL uses async driver (+asyncpg, +aiomysql, +aiosqlite)")
        print("2. Install required async driver: pip install asyncpg aiomysql aiosqlite")
        print("3. Check database supports async operations (PostgreSQL, MySQL, SQLite)")
        print("4. Review async configuration in src/database/README.md")
        raise


if __name__ == "__main__":
    """Run modern async-native database initialization."""
    asyncio.run(main())