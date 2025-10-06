"""
Tests for training manager.
"""
import pytest
import tempfile
import json
from pathlib import Path
from rave_gui.core.database import Database
from rave_gui.backend.training import TrainingManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    
    db = Database(db_path)
    yield db
    
    db.close()
    db_path.unlink()


@pytest.fixture
def training_manager(temp_db):
    """Create a training manager instance."""
    return TrainingManager(temp_db)


@pytest.fixture
def sample_dataset(temp_db):
    """Create a sample dataset for testing."""
    cursor = temp_db.execute(
        """INSERT INTO datasets 
           (name, path, num_samples, channels, sample_rate) 
           VALUES (?, ?, ?, ?, ?)""",
        ("Test Dataset", "/path/to/dataset", 1000, 2, 44100)
    )
    return cursor.lastrowid


def test_start_training(training_manager, sample_dataset):
    """Test starting a training run."""
    config = {
        'name': 'test_training',
        'dataset_id': sample_dataset,
        'dataset_path': '/path/to/dataset',
        'config': 'v2',
        'max_steps': 10000
    }
    
    experiment_id = training_manager.start_training(config)
    
    assert experiment_id is not None
    assert experiment_id > 0
    
    # Verify experiment was created
    experiment = training_manager.get_experiment(experiment_id)
    assert experiment is not None
    assert experiment['name'] == 'test_training'
    assert experiment['status'] == 'running'
    assert experiment['dataset_id'] == sample_dataset


def test_get_experiment(training_manager, sample_dataset):
    """Test retrieving an experiment."""
    config = {
        'name': 'test_experiment',
        'dataset_id': sample_dataset,
        'dataset_path': '/path/to/dataset',
        'config': 'v2'
    }
    
    experiment_id = training_manager.start_training(config)
    experiment = training_manager.get_experiment(experiment_id)
    
    assert experiment is not None
    assert experiment['id'] == experiment_id
    assert experiment['name'] == 'test_experiment'
    assert isinstance(experiment['config'], dict)


def test_list_experiments(training_manager, sample_dataset):
    """Test listing experiments."""
    # Create multiple experiments
    for i in range(3):
        config = {
            'name': f'experiment_{i}',
            'dataset_id': sample_dataset,
            'dataset_path': '/path/to/dataset',
            'config': 'v2'
        }
        training_manager.start_training(config)
    
    experiments = training_manager.list_experiments()
    
    assert len(experiments) == 3
    assert all(exp['name'].startswith('experiment_') for exp in experiments)


def test_update_experiment_status(training_manager, sample_dataset):
    """Test updating experiment status."""
    config = {
        'name': 'status_test',
        'dataset_id': sample_dataset,
        'dataset_path': '/path/to/dataset',
        'config': 'v2'
    }
    
    experiment_id = training_manager.start_training(config)
    
    # Update status to completed
    training_manager.update_experiment_status(experiment_id, 'completed', '2024-01-01T12:00:00')
    
    experiment = training_manager.get_experiment(experiment_id)
    assert experiment['status'] == 'completed'
    assert experiment['completed_at'] == '2024-01-01T12:00:00'


def test_update_training_metrics(training_manager, sample_dataset):
    """Test updating training metrics."""
    config = {
        'name': 'metrics_test',
        'dataset_id': sample_dataset,
        'dataset_path': '/path/to/dataset',
        'config': 'v2'
    }
    
    experiment_id = training_manager.start_training(config)
    
    # Update metrics
    metrics = {
        'step': 1000,
        'loss': 0.5,
        'val_loss': 0.6,
        'lr': 0.0001
    }
    training_manager.update_training_metrics(experiment_id, metrics)
    
    # Verify metrics were saved
    retrieved_metrics = training_manager.get_training_metrics(experiment_id)
    assert retrieved_metrics['step'] == 1000
    assert retrieved_metrics['loss'] == 0.5
    assert retrieved_metrics['val_loss'] == 0.6
    assert retrieved_metrics['lr'] == 0.0001


def test_get_training_metrics(training_manager, sample_dataset):
    """Test getting training metrics."""
    config = {
        'name': 'get_metrics_test',
        'dataset_id': sample_dataset,
        'dataset_path': '/path/to/dataset',
        'config': 'v2'
    }
    
    experiment_id = training_manager.start_training(config)
    
    # Initially should return empty dict
    metrics = training_manager.get_training_metrics(experiment_id)
    assert metrics == {}
    
    # Update and retrieve
    new_metrics = {'step': 500, 'loss': 0.3}
    training_manager.update_training_metrics(experiment_id, new_metrics)
    
    metrics = training_manager.get_training_metrics(experiment_id)
    assert metrics == new_metrics


def test_register_and_unregister_process(training_manager, sample_dataset):
    """Test process registration."""
    config = {
        'name': 'process_test',
        'dataset_id': sample_dataset,
        'dataset_path': '/path/to/dataset',
        'config': 'v2'
    }
    
    experiment_id = training_manager.start_training(config)
    
    # Mock process object
    class MockProcess:
        def stop(self):
            pass
    
    process = MockProcess()
    
    # Register process
    training_manager.register_process(experiment_id, process)
    assert experiment_id in training_manager.active_processes
    
    # Unregister process
    training_manager.unregister_process(experiment_id)
    assert experiment_id not in training_manager.active_processes


def test_stop_training(training_manager, sample_dataset):
    """Test stopping a training run."""
    config = {
        'name': 'stop_test',
        'dataset_id': sample_dataset,
        'dataset_path': '/path/to/dataset',
        'config': 'v2'
    }
    
    experiment_id = training_manager.start_training(config)
    
    # Mock process
    class MockProcess:
        def __init__(self):
            self.stopped = False
            
        def stop(self):
            self.stopped = True
    
    process = MockProcess()
    training_manager.register_process(experiment_id, process)
    
    # Stop training
    result = training_manager.stop_training(experiment_id)
    
    assert result is True
    assert process.stopped is True
    assert experiment_id not in training_manager.active_processes
    
    # Verify status was updated
    experiment = training_manager.get_experiment(experiment_id)
    assert experiment['status'] == 'stopped'


def test_stop_nonexistent_training(training_manager):
    """Test stopping a non-existent training run."""
    result = training_manager.stop_training(999)
    assert result is False
