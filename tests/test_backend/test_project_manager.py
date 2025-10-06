"""
Tests for project manager backend.
"""
import pytest
import tempfile
from pathlib import Path
from rave_gui.core.database import Database
from rave_gui.backend.project import ProjectManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path)
        yield db
        db.close()


@pytest.fixture
def project_manager(temp_db):
    """Create a project manager with temporary database."""
    return ProjectManager(temp_db)


def test_create_project(project_manager):
    """Test creating a new project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_id = project_manager.create_project("Test Project", tmpdir)
        
        assert project_id is not None
        assert isinstance(project_id, int)
        
        # Verify project was created
        project = project_manager.get_project(project_id)
        assert project is not None
        assert project['name'] == "Test Project"
        assert project['path'] == tmpdir


def test_create_duplicate_project(project_manager):
    """Test that creating duplicate project raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_manager.create_project("Test Project", tmpdir)
        
        with pytest.raises(ValueError, match="already exists"):
            project_manager.create_project("Test Project", tmpdir)


def test_get_project(project_manager):
    """Test retrieving a project by ID."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_id = project_manager.create_project("Test Project", tmpdir)
        
        project = project_manager.get_project(project_id)
        assert project is not None
        assert project['id'] == project_id
        assert project['name'] == "Test Project"


def test_get_nonexistent_project(project_manager):
    """Test retrieving a non-existent project."""
    project = project_manager.get_project(9999)
    assert project is None


def test_get_project_by_name(project_manager):
    """Test retrieving a project by name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_manager.create_project("Test Project", tmpdir)
        
        project = project_manager.get_project_by_name("Test Project")
        assert project is not None
        assert project['name'] == "Test Project"


def test_list_projects(project_manager):
    """Test listing all projects."""
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            project_manager.create_project("Project 1", tmpdir1)
            project_manager.create_project("Project 2", tmpdir2)
            
            projects = project_manager.list_projects()
            assert len(projects) == 2
            assert any(p['name'] == "Project 1" for p in projects)
            assert any(p['name'] == "Project 2" for p in projects)


def test_delete_project(project_manager):
    """Test deleting a project."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_id = project_manager.create_project("Test Project", tmpdir)
        
        result = project_manager.delete_project(project_id)
        assert result is True
        
        # Verify project was deleted
        project = project_manager.get_project(project_id)
        assert project is None


def test_update_project(project_manager):
    """Test updating a project."""
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            project_id = project_manager.create_project("Test Project", tmpdir1)
            
            # Update name
            result = project_manager.update_project(project_id, name="Updated Project")
            assert result is True
            
            project = project_manager.get_project(project_id)
            assert project['name'] == "Updated Project"
            
            # Update path
            result = project_manager.update_project(project_id, path=tmpdir2)
            assert result is True
            
            project = project_manager.get_project(project_id)
            assert project['path'] == tmpdir2
