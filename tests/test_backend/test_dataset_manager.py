"""
Tests for dataset manager backend.
"""
import pytest
import tempfile
from pathlib import Path
from rave_gui.core.database import Database
from rave_gui.backend.dataset import DatasetManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path)
        yield db
        db.close()


@pytest.fixture
def dataset_manager(temp_db):
    """Create a dataset manager with temporary database."""
    return DatasetManager(temp_db)


def test_create_dataset(dataset_manager):
    """Test creating a new dataset."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'name': 'Test Dataset',
            'path': tmpdir,
            'channels': 1,
            'sample_rate': 44100,
            'num_samples': 1000
        }
        
        dataset_id = dataset_manager.create_dataset(config)
        
        assert dataset_id is not None
        assert isinstance(dataset_id, int)
        
        # Verify dataset was created
        dataset = dataset_manager.get_dataset(dataset_id)
        assert dataset is not None
        assert dataset['name'] == 'Test Dataset'
        assert dataset['path'] == tmpdir
        assert dataset['channels'] == 1
        assert dataset['sample_rate'] == 44100


def test_create_dataset_missing_name(dataset_manager):
    """Test that creating dataset without name raises error."""
    config = {
        'path': '/tmp/test',
        'channels': 1,
        'sample_rate': 44100
    }
    
    with pytest.raises(ValueError, match="Dataset name is required"):
        dataset_manager.create_dataset(config)


def test_create_dataset_missing_path(dataset_manager):
    """Test that creating dataset without path raises error."""
    config = {
        'name': 'Test Dataset',
        'channels': 1,
        'sample_rate': 44100
    }
    
    with pytest.raises(ValueError, match="Dataset path is required"):
        dataset_manager.create_dataset(config)


def test_get_dataset(dataset_manager):
    """Test retrieving a dataset by ID."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'name': 'Test Dataset',
            'path': tmpdir,
            'channels': 2,
            'sample_rate': 48000
        }
        
        dataset_id = dataset_manager.create_dataset(config)
        
        dataset = dataset_manager.get_dataset(dataset_id)
        assert dataset is not None
        assert dataset['id'] == dataset_id
        assert dataset['name'] == 'Test Dataset'
        assert dataset['channels'] == 2
        assert dataset['sample_rate'] == 48000


def test_get_nonexistent_dataset(dataset_manager):
    """Test retrieving a non-existent dataset."""
    dataset = dataset_manager.get_dataset(9999)
    assert dataset is None


def test_list_datasets(dataset_manager):
    """Test listing all datasets."""
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            config1 = {
                'name': 'Dataset 1',
                'path': tmpdir1,
                'channels': 1,
                'sample_rate': 44100
            }
            config2 = {
                'name': 'Dataset 2',
                'path': tmpdir2,
                'channels': 2,
                'sample_rate': 48000
            }
            
            dataset_manager.create_dataset(config1)
            dataset_manager.create_dataset(config2)
            
            datasets = dataset_manager.list_datasets()
            assert len(datasets) == 2
            assert any(d['name'] == 'Dataset 1' for d in datasets)
            assert any(d['name'] == 'Dataset 2' for d in datasets)


def test_list_datasets_by_project(dataset_manager, temp_db):
    """Test listing datasets filtered by project."""
    # Create a project first
    cursor = temp_db.execute(
        "INSERT INTO projects (name, path) VALUES (?, ?)",
        ("Test Project", "/tmp/test")
    )
    project_id = cursor.lastrowid
    
    with tempfile.TemporaryDirectory() as tmpdir1:
        with tempfile.TemporaryDirectory() as tmpdir2:
            # Create datasets with and without project
            config1 = {
                'name': 'Dataset 1',
                'path': tmpdir1,
                'project_id': project_id,
                'channels': 1,
                'sample_rate': 44100
            }
            config2 = {
                'name': 'Dataset 2',
                'path': tmpdir2,
                'channels': 1,
                'sample_rate': 44100
            }
            
            dataset_manager.create_dataset(config1)
            dataset_manager.create_dataset(config2)
            
            # List datasets for project
            project_datasets = dataset_manager.list_datasets(project_id)
            assert len(project_datasets) == 1
            assert project_datasets[0]['name'] == 'Dataset 1'


def test_delete_dataset(dataset_manager):
    """Test deleting a dataset."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'name': 'Test Dataset',
            'path': tmpdir,
            'channels': 1,
            'sample_rate': 44100
        }
        
        dataset_id = dataset_manager.create_dataset(config)
        
        result = dataset_manager.delete_dataset(dataset_id)
        assert result is True
        
        # Verify dataset was deleted
        dataset = dataset_manager.get_dataset(dataset_id)
        assert dataset is None


def test_get_dataset_stats(dataset_manager):
    """Test getting dataset statistics."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'name': 'Test Dataset',
            'path': tmpdir,
            'channels': 2,
            'sample_rate': 44100,
            'num_samples': 44100  # 1 second of audio
        }
        
        dataset_id = dataset_manager.create_dataset(config)
        
        stats = dataset_manager.get_dataset_stats(dataset_id)
        assert stats['total_samples'] == 44100
        assert stats['channels'] == 2
        assert stats['sample_rate'] == 44100
        assert abs(stats['duration_seconds'] - 1.0) < 0.01  # Approximately 1 second


def test_get_dataset_stats_no_samples(dataset_manager):
    """Test getting statistics for dataset with no samples."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'name': 'Test Dataset',
            'path': tmpdir,
            'channels': 1,
            'sample_rate': 44100
        }
        
        dataset_id = dataset_manager.create_dataset(config)
        
        stats = dataset_manager.get_dataset_stats(dataset_id)
        assert stats['total_samples'] == 0
        assert stats['duration_seconds'] == 0


def test_get_dataset_stats_nonexistent(dataset_manager):
    """Test getting statistics for non-existent dataset."""
    stats = dataset_manager.get_dataset_stats(9999)
    assert stats == {}


def test_create_dataset_with_defaults(dataset_manager):
    """Test creating dataset with default values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {
            'name': 'Test Dataset',
            'path': tmpdir
        }
        
        dataset_id = dataset_manager.create_dataset(config)
        dataset = dataset_manager.get_dataset(dataset_id)
        
        # Check defaults
        assert dataset['channels'] == 1
        assert dataset['sample_rate'] == 44100
