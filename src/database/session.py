"""Database session management and dependency injection."""

from contextlib import contextmanager
from typing import Generator, Iterator
from sqlalchemy.orm import sessionmaker, Session
from .engine import engine


# Session factory
SessionLocal = sessionmaker(
  bind=engine,
  autocommit=False,
  autoflush=False,
  expire_on_commit=False,
)


def get_session() -> Generator[Session, None, None]:
  """
  Dependency injection function for FastAPI.
  
  Usage:
    @app.get("/users/")
    def get_users(session: Session = Depends(get_session)):
        return session.execute(select(User)).scalars().all()
  """
  session = SessionLocal()
  try:
    yield session
    session.commit()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()


@contextmanager
def session_scope() -> Iterator[Session]:
  """
  Context manager for database sessions.
  
  Usage:
    with session_scope() as session:
        user = User(username="john_doe")
        session.add(user)
        # Automatic commit on success, rollback on exception
  """
  session = SessionLocal()
  try:
    yield session
    session.commit()
  except Exception:
    session.rollback()
    raise
  finally:
    session.close()