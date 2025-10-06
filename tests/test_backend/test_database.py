"""
Example test for database operations.
"""
import pytest
import tempfile
from pathlib import Path
from rave_gui.core.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    db = Database(db_path)
    yield db
    
    db.close()
    db_path.unlink()


def test_database_initialization(temp_db):
    """Test that database schema is created."""
    # Check that tables exist
    tables = temp_db.fetch_all(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    table_names = [t['name'] for t in tables]
    
    assert 'projects' in table_names
    assert 'datasets' in table_names
    assert 'experiments' in table_names
    assert 'models' in table_names
    assert 'exports' in table_names


def test_database_crud_operations(temp_db):
    """Test basic CRUD operations."""
    # Insert a project
    cursor = temp_db.execute(
        "INSERT INTO projects (name, path) VALUES (?, ?)",
        ("Test Project", "/path/to/project")
    )
    project_id = cursor.lastrowid
    
    # Read the project
    project = temp_db.fetch_one(
        "SELECT * FROM projects WHERE id = ?",
        (project_id,)
    )
    
    assert project is not None
    assert project['name'] == "Test Project"
    assert project['path'] == "/path/to/project"
