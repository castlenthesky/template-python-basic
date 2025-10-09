"""Database-agnostic custom types for SQLAlchemy."""

from uuid import UUID
from sqlalchemy import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    
    Uses native UUID type for PostgreSQL and CHAR(36) for other databases
    like SQLite, MySQL, and DuckDB. Automatically handles conversion
    between UUID objects and string representation.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load the appropriate type for the specific database dialect."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        """Process UUID values before storing in database."""
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value  # PostgreSQL handles UUID objects natively
        else:
            return str(value)  # Convert to string for other databases

    def process_result_value(self, value, dialect):
        """Process values when retrieving from database."""
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value  # PostgreSQL returns UUID objects
        else:
            return UUID(value)  # Convert string back to UUID object