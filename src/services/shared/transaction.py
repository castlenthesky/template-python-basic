"""Transaction management utilities for services."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


@asynccontextmanager
async def transaction_scope(
    session: AsyncSession, 
    auto_commit: bool = True,
    rollback_on_exception: bool = True
) -> AsyncGenerator[AsyncSession, None]:
    """
    Transaction context manager for database operations.
    
    Args:
        session: Database session to manage
        auto_commit: Whether to automatically commit on successful completion
        rollback_on_exception: Whether to rollback on exceptions
        
    Yields:
        The database session within a transaction scope
        
    Raises:
        Exception: Re-raises any exceptions that occur within the transaction
    """
    try:
        yield session
        if auto_commit:
            await session.commit()
            logger.debug("Transaction committed successfully")
    except Exception as e:
        if rollback_on_exception:
            await session.rollback()
            logger.warning(f"Transaction rolled back due to error: {e}")
        raise
    finally:
        # Session cleanup is handled by the dependency injection system
        pass


class TransactionalService:
    """Base class for services that need transaction management."""
    
    async def execute_in_transaction(
        self,
        session: AsyncSession,
        operation,
        *args,
        auto_commit: bool = True,
        **kwargs
    ):
        """
        Execute an operation within a transaction scope.
        
        Args:
            session: Database session
            operation: Callable to execute within transaction
            *args: Arguments to pass to operation
            auto_commit: Whether to auto-commit the transaction
            **kwargs: Keyword arguments to pass to operation
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: Any exception raised by the operation
        """
        async with transaction_scope(session, auto_commit=auto_commit):
            return await operation(session, *args, **kwargs)