"""Modern async-native database example demonstrating production patterns.

This example showcases the async-native database operations following 
modern async-first architecture principles:
- Async-native database connection and session management
- Repository pattern for async data access layer
- Service layer for async business logic
- Modern async session handling with context managers
- Production-ready async error handling and transactions
"""

import asyncio
from sqlmodel import SQLModel

from src.database import get_async_db_connection
from src.database.engine import get_async_engine
from src.database.models.task import TaskCreate
from src.database.models.user import UserCreate, UserRead
from src.services.users.service import UserService
from src.services.tasks.service import TaskService


async def create_async_tables():
    """Create all database tables using async-native patterns."""
    print("Creating database tables with async-native architecture...")
    
    async_engine = get_async_engine()
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    print("✅ Async tables created successfully!")


async def async_database_example():
    """Main async-native database example demonstrating modern patterns."""

    print("\n🚀 Async-Native Database Operations - Modern Architecture")
    print("=" * 60)

    # Create tables using async-native patterns
    await create_async_tables()
    
    # Get async database connection for high-performance operations
    async_db = get_async_db_connection()
    
    # Initialize async service layer for business logic
    user_service = UserService()
    task_service = TaskService()

    # Example 1: Async data operations with repository pattern
    print("\n📝 Example 1: Async data operations with repository pattern")

    async with async_db.create_session() as session:
        try:
            # Create user through service layer within async session
            user_create = UserCreate(username="async_native_user")
            user = await user_service.create_user(session, user_create)
            print(f"✅ User created via service layer in async session: {user}")

            # Create tasks demonstrating async operations with modern architecture
            task_creates = [
                TaskCreate(
                    title="Master Async-Native Architecture", 
                    description="Learn modern async-native database patterns in Python", 
                    user_id=user.id
                ),
                TaskCreate(
                    title="Implement Async Repository Pattern",
                    description="Build high-performance async data access layer",
                    user_id=user.id,
                ),
                TaskCreate(
                    title="Design Async Service Layer",
                    description="Create async business logic layer for scalability",
                    user_id=user.id,
                ),
            ]

            created_tasks = []
            for task_create in task_creates:
                task = task_service.create(session, task_create)
                created_tasks.append(task)
                print(f"✅ Task created via service layer in async session: {task}")

        except Exception as e:
            print(f"❌ Error in async data operations: {e}")
            raise

    # Example 2: Async read operations with modern patterns
    print("\n📖 Example 2: Async read operations and status updates")

    async with async_db.create_session() as session:
        try:
            # Find user using service layer within async session
            user = user_service.get_by_username(session, "async_native_user")
            if user:
                print(f"🔍 User retrieved via service layer: {user}")

                # Get user's tasks through service layer within async session
                user_tasks = task_service.get_by_user(session, user.id)
                print(f"📋 User has {len(user_tasks)} tasks (via service layer in async session):")
                for task in user_tasks:
                    print(f"  - {task}")

                # Demonstrate business logic through service layer within async session
                if user_tasks:
                    completed_task = task_service.mark_completed(session, user_tasks[0].id)
                    print(f"✅ Task completed via service layer in async session: {completed_task}")

                    # Update second task status
                    if len(user_tasks) > 1:
                        in_progress_task = task_service.mark_in_progress(session, user_tasks[1].id)
                        print(f"🔄 Task status updated via service layer in async session: {in_progress_task}")

        except Exception as e:
            print(f"❌ Error in async read operations: {e}")
            raise

    # Example 3: Advanced async queries demonstrating repository pattern
    print("\n🔍 Example 3: Advanced async queries and data filtering")

    async with async_db.create_session() as session:
        try:
            # Get multiple users through service layer within async session
            all_users = user_service.get_multi(session, limit=10)
            print(f"👥 Total users (via service layer in async session): {len(all_users)}")

            # Get completed tasks using service layer within async session
            completed_tasks = task_service.get_completed_tasks(session)
            print(f"✅ Completed tasks (via service layer in async session): {len(completed_tasks)}")

            # Get pending tasks through service layer within async session
            pending_tasks = task_service.get_pending_tasks(session)
            print(f"⏳ Pending tasks (via service layer in async session): {len(pending_tasks)}")

            # Search tasks through service layer within async session
            search_results = task_service.search_by_title(session, "Architecture")
            print(f"🔎 Tasks matching 'Architecture' (via service layer in async session): {len(search_results)}")

            # Demonstrate relationship loading through service layer within async session
            if all_users:
                user_with_tasks = user_service.get_user_with_tasks(session, all_users[0].id)
                if user_with_tasks:
                    print(f"👤 User with tasks loaded (via service layer in async session): {user_with_tasks.username} ({len(user_with_tasks.tasks)} tasks)")

        except Exception as e:
            print(f"❌ Error in advanced async queries: {e}")
            raise

    # Example 4: Async session connectivity test
    print("\n🔗 Example 4: Async session connectivity and performance test")

    async with async_db.create_session() as session:
        try:
            # Test async connectivity with native SQL
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1 as connectivity_test"))
            test_value = result.scalar()
            print(f"✅ Async connectivity verified: SELECT 1 = {test_value}")
            
            # Test async health check
            is_healthy = await async_db.health_check()
            print(f"💓 Async database health: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}")

        except Exception as e:
            print(f"❌ Error in async connectivity test: {e}")
            raise

    # Example 5: Async resource cleanup
    print("\n🧹 Example 5: Async resource management")
    try:
        await async_db.close_connections()
        print("✅ Async connections and pools closed successfully")
    except Exception as e:
        print(f"⚠️  Warning during async resource cleanup: {e}")

    print("\n🎉 Async-native database operations with modern architecture completed!")
    print("=" * 70)


async def cleanup_async_example_data():
    """Clean up example data using async service layer."""
    print("\n🧹 Cleaning up async example data...")
    
    async_db = get_async_db_connection()
    user_service = UserService()

    async with async_db.create_session() as session:
        try:
            # Get all users through service layer within async session (cascade deletes tasks)
            users = user_service.get_multi(session)
            for user in users:
                user_service.delete(session, user.id)
                print(f"🗑️ User deleted via service layer in async session: {user.username}")

        except Exception as e:
            print(f"❌ Error during async cleanup: {e}")
            raise

    print("✅ Async data cleanup completed!")


async def main():
    """Main async function for database example."""
    try:
        # Run comprehensive async-native database example
        await async_database_example()

        # Ask user about cleanup (handle non-interactive environments)
        try:
            response = input("\nDo you want to clean up the async example data? (y/N): ")
            if response.lower().startswith("y"):
                await cleanup_async_example_data()
            else:
                print("Async example data retained for inspection.")
                print("💡 Note: Data is fully async-native and optimized for modern applications.")
        except EOFError:
            print("Running in non-interactive mode. Async example data retained for inspection.")

    except Exception as e:
        print(f"\n💥 Fatal error in async-native operations: {e}")
        print("💡 Async troubleshooting guide:")
        print("1. Verify DATABASE_URL uses async driver (+asyncpg, +aiomysql, +aiosqlite)")
        print("2. Install required async driver: pip install asyncpg aiomysql aiosqlite")
        print("3. Check database supports async operations (PostgreSQL, MySQL, SQLite)")
        print("4. Review async configuration in src/database/README.md")
        raise


if __name__ == "__main__":
    """Run async-native database example demonstrating modern architecture patterns."""
    asyncio.run(main())