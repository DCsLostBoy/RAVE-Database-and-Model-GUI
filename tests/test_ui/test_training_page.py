"""
Tests for training page UI.
"""
import pytest
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from rave_gui.core.database import Database
from rave_gui.ui.pages.training import TrainingPage


@pytest.fixture
def qapp():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


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
def training_page(qapp, temp_db):
    """Create a training page instance."""
    return TrainingPage(temp_db)


def test_training_page_initialization(training_page):
    """Test that training page initializes correctly."""
    assert training_page is not None
    assert training_page.training_manager is not None
    assert training_page.experiments_table is not None
    assert training_page.metrics_plot is not None


def test_new_training_button_exists(training_page):
    """Test that new training button exists."""
    assert training_page.new_training_btn is not None
    assert training_page.new_training_btn.text() == "New Training"


def test_experiments_table_structure(training_page):
    """Test experiments table has correct columns."""
    assert training_page.experiments_table.columnCount() == 5
    
    headers = []
    for i in range(training_page.experiments_table.columnCount()):
        header = training_page.experiments_table.horizontalHeaderItem(i)
        if header:
            headers.append(header.text())
    
    # Check that expected headers are present
    assert len(headers) == 5


def test_load_empty_experiments(training_page):
    """Test loading experiments when database is empty."""
    training_page.load_experiments()
    assert training_page.experiments_table.rowCount() == 0


def test_load_experiments_with_data(training_page, temp_db):
    """Test loading experiments with data."""
    # Create a dataset first
    cursor = temp_db.execute(
        """INSERT INTO datasets 
           (name, path, num_samples, channels, sample_rate) 
           VALUES (?, ?, ?, ?, ?)""",
        ("Test Dataset", "/path/to/dataset", 1000, 2, 44100)
    )
    dataset_id = cursor.lastrowid
    
    # Create an experiment
    experiment_id = training_page.training_manager.start_training({
        'name': 'test_experiment',
        'dataset_id': dataset_id,
        'dataset_path': '/path/to/dataset',
        'config': 'v2'
    })
    
    # Load experiments
    training_page.load_experiments()
    
    assert training_page.experiments_table.rowCount() == 1


def test_metrics_plot_exists(training_page):
    """Test that metrics plot widget exists."""
    assert training_page.metrics_plot is not None


def test_log_viewer_exists(training_page):
    """Test that log viewer exists."""
    assert training_page.log_viewer is not None
    assert training_page.log_viewer.isReadOnly()


def test_progress_bar_initially_hidden(training_page):
    """Test that progress bar is initially hidden."""
    assert not training_page.progress_bar.isVisible()


def test_on_training_output(training_page):
    """Test handling of training output."""
    training_page.selected_experiment_id = 1
    training_page.on_training_output(1, "Test log line")
    
    text = training_page.log_viewer.toPlainText()
    assert "Test log line" in text


def test_on_metrics_update(training_page, temp_db):
    """Test handling of metrics updates."""
    # Create experiment
    cursor = temp_db.execute(
        """INSERT INTO datasets 
           (name, path, num_samples, channels, sample_rate) 
           VALUES (?, ?, ?, ?, ?)""",
        ("Test Dataset", "/path/to/dataset", 1000, 2, 44100)
    )
    dataset_id = cursor.lastrowid
    
    experiment_id = training_page.training_manager.start_training({
        'name': 'test_experiment',
        'dataset_id': dataset_id,
        'dataset_path': '/path/to/dataset',
        'config': 'v2'
    })
    
    # Update metrics
    metrics = {'step': 1000, 'loss': 0.5}
    training_page.on_metrics_update(experiment_id, metrics)
    
    # Verify metrics were saved
    saved_metrics = training_page.training_manager.get_training_metrics(experiment_id)
    assert saved_metrics['step'] == 1000
    assert saved_metrics['loss'] == 0.5
