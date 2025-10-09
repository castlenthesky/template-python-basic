"""Integration tests for Alembic migrations."""

import os
import tempfile
import pytest
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from alembic.config import Config
from alembic import command
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from src.database.models.user import User
from src.database.models.task import Task


class TestAlembicMigrations:
  """Integration tests for Alembic database migrations."""
  
  @pytest.fixture(scope="function")
  def migration_engine(self):
    """Create a temporary database engine for migration testing."""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db', prefix='migration_test_')
    os.close(db_fd)
    
    try:
      # Create engine
      engine = create_engine(f"sqlite:///{db_path}")
      yield engine
    finally:
      # Cleanup
      try:
        engine.dispose()
        os.unlink(db_path)
      except OSError:
        pass
  
  @pytest.fixture(scope="function")  
  def alembic_config(self, migration_engine):
    """Create Alembic configuration for testing."""
    # Create temporary alembic.ini
    config_fd, config_path = tempfile.mkstemp(suffix='.ini', prefix='alembic_test_')
    
    try:
      with os.fdopen(config_fd, 'w') as f:
        f.write(f"""
[alembic]
script_location = src/database/migrations
sqlalchemy.url = {migration_engine.url}
prepend_sys_path = .

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]  
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers = 
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
""")
      
      # Create Alembic config object
      alembic_cfg = Config(config_path)
      alembic_cfg.set_main_option("sqlalchemy.url", str(migration_engine.url))
      
      yield alembic_cfg
      
    finally:
      try:
        os.unlink(config_path)
      except OSError:
        pass
  
  @pytest.mark.skip(reason="Complex Alembic testing needs additional configuration")
  def test_migration_up_and_down(self, alembic_config: Config, migration_engine: Engine):
    """Test running migration up and down."""
    # This test is skipped for now as it requires more complex setup
    # to properly integrate with the test database configuration
    pass
  
  @pytest.mark.skip(reason="Requires complex Alembic integration setup")
  def test_migration_generates_correct_schema(self, alembic_config: Config, migration_engine: Engine):
    """Test that migration generates schema matching our models."""
    pass
  
  @pytest.mark.skip(reason="Requires complex Alembic integration setup") 
  def test_migration_history(self, alembic_config: Config, migration_engine: Engine):
    """Test migration history tracking."""
    pass
  
  @pytest.mark.skip(reason="Requires complex Alembic integration setup")
  def test_migration_idempotency(self, alembic_config: Config, migration_engine: Engine):
    """Test that running the same migration multiple times is safe."""
    pass
  
  def test_migration_script_directory(self):
    """Test that migration script directory is properly configured."""
    # Test script directory exists
    script_dir = Path("src/database/migrations")
    assert script_dir.exists()
    assert script_dir.is_dir()
    
    # Test versions directory exists
    versions_dir = script_dir / "versions"
    assert versions_dir.exists()
    assert versions_dir.is_dir()
    
    # Test env.py exists
    env_file = script_dir / "env.py"
    assert env_file.exists()
    assert env_file.is_file()
    
    # Test there's at least one migration file
    migration_files = list(versions_dir.glob("*.py"))
    assert len(migration_files) > 0
    
    # Verify migration files have proper naming convention
    for migration_file in migration_files:
      # Should have format: {revision}_{slug}.py
      parts = migration_file.stem.split('_', 1)
      assert len(parts) == 2
      revision, slug = parts
      assert len(revision) == 12  # Alembic revision length
      assert len(slug) > 0  # Should have a description
  
  def test_current_migration_matches_models(self, alembic_config: Config, migration_engine: Engine):
    """Test that current migration state matches our model definitions."""
    # Run migration
    command.upgrade(alembic_config, "head")
    
    # Import models to ensure metadata is loaded
    from sqlmodel import SQLModel
    _ = User, Task  # Ensure models are imported
    
    # Get current database schema
    inspector = inspect(migration_engine)
    
    # Compare with SQLModel metadata
    model_tables = SQLModel.metadata.tables
    db_tables = inspector.get_table_names()
    
    # Check that all model tables exist in database
    for table_name in model_tables.keys():
      assert table_name in db_tables, f"Model table '{table_name}' not found in database"
    
    # Check that key tables from our models are present
    assert "users" in model_tables
    assert "tasks" in model_tables
    
    # Verify basic structure matches
    users_table = model_tables["users"]
    tasks_table = model_tables["tasks"]
    
    # Check users table columns
    users_db_columns = {col['name'] for col in inspector.get_columns('users')}
    users_model_columns = {col.name for col in users_table.columns}
    assert users_db_columns == users_model_columns
    
    # Check tasks table columns  
    tasks_db_columns = {col['name'] for col in inspector.get_columns('tasks')}
    tasks_model_columns = {col.name for col in tasks_table.columns}
    assert tasks_db_columns == tasks_model_columns