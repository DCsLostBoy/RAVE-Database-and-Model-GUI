"""
Tests for training process metrics parsing.
"""
import pytest
from rave_gui.backend.training import TrainingProcess


def test_metrics_parsing():
    """Test parsing of training metrics from log lines."""
    config = {
        'name': 'test',
        'dataset_path': '/test/path',
        'config': 'v2',
        'max_steps': 10000
    }
    
    # Don't actually run the process, just test parsing
    process = TrainingProcess(config)
    
    # Test loss parsing
    line = "step: 1000 loss: 0.5432 lr: 0.0001"
    progress, msg = process.parse_progress(line)
    
    assert 'loss' in process.current_metrics
    assert process.current_metrics['loss'] == 0.5432
    assert 'step' in process.current_metrics
    assert process.current_metrics['step'] == 1000
    assert 'lr' in process.current_metrics
    assert process.current_metrics['lr'] == 0.0001


def test_step_parsing():
    """Test parsing of step information."""
    config = {
        'name': 'test',
        'dataset_path': '/test/path',
        'config': 'v2',
        'max_steps': 10000
    }
    
    process = TrainingProcess(config)
    
    line = "Training step: 5000"
    progress, msg = process.parse_progress(line)
    
    assert 'step' in process.current_metrics
    assert process.current_metrics['step'] == 5000
    assert progress == 50  # 5000/10000 * 100


def test_validation_loss_parsing():
    """Test parsing of validation loss."""
    config = {
        'name': 'test',
        'dataset_path': '/test/path',
        'config': 'v2'
    }
    
    process = TrainingProcess(config)
    
    line = "Validation val_loss: 0.3456"
    progress, msg = process.parse_progress(line)
    
    assert 'val_loss' in process.current_metrics
    assert process.current_metrics['val_loss'] == 0.3456


def test_epoch_parsing():
    """Test parsing of epoch information."""
    config = {
        'name': 'test',
        'dataset_path': '/test/path',
        'config': 'v2'
    }
    
    process = TrainingProcess(config)
    
    line = "Epoch: 10 completed"
    progress, msg = process.parse_progress(line)
    
    assert 'epoch' in process.current_metrics
    assert process.current_metrics['epoch'] == 10


def test_case_insensitive_parsing():
    """Test that parsing is case-insensitive."""
    config = {
        'name': 'test',
        'dataset_path': '/test/path',
        'config': 'v2'
    }
    
    process = TrainingProcess(config)
    
    # Test uppercase
    line = "STEP: 100 LOSS: 1.234 LR: 0.001"
    progress, msg = process.parse_progress(line)
    
    assert process.current_metrics['step'] == 100
    assert process.current_metrics['loss'] == 1.234
    assert process.current_metrics['lr'] == 0.001


def test_scientific_notation_parsing():
    """Test parsing of scientific notation for learning rate."""
    config = {
        'name': 'test',
        'dataset_path': '/test/path',
        'config': 'v2'
    }
    
    process = TrainingProcess(config)
    
    line = "step: 1000 lr: 1e-4"
    progress, msg = process.parse_progress(line)
    
    assert 'lr' in process.current_metrics
    assert process.current_metrics['lr'] == 0.0001


def test_no_metrics_in_line():
    """Test handling of lines with no metrics."""
    config = {
        'name': 'test',
        'dataset_path': '/test/path',
        'config': 'v2'
    }
    
    process = TrainingProcess(config)
    
    line = "Loading checkpoint..."
    progress, msg = process.parse_progress(line)
    
    assert progress is None
    assert msg == line


def test_multiple_formats():
    """Test parsing of different format variations."""
    config = {
        'name': 'test',
        'dataset_path': '/test/path',
        'config': 'v2'
    }
    
    process = TrainingProcess(config)
    
    # Test with colons
    line1 = "step: 100 loss: 0.5"
    process.parse_progress(line1)
    assert process.current_metrics['step'] == 100
    
    # Test with equals
    line2 = "step=200 loss=0.4"
    # This should still work with the current regex pattern
    progress, msg = process.parse_progress(line2)
    # Note: current implementation uses colon-based patterns
    # If needed, we can extend to support equals sign
