"""
Qt signals for cross-component communication.
"""
from PyQt6.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    """Global application signals for cross-component communication.
    
    This is a singleton class - use AppSignals() to get the instance.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    # General signals
    status_message = pyqtSignal(str)  # message
    error_occurred = pyqtSignal(str, str)  # title, message
    
    # Dataset signals
    dataset_created = pyqtSignal(int, str)  # dataset_id, name
    dataset_deleted = pyqtSignal(int)  # dataset_id
    dataset_preprocessing_progress = pyqtSignal(int, int, str)  # dataset_id, percentage, message
    
    # Training signals
    training_started = pyqtSignal(int, str)  # experiment_id, name
    training_stopped = pyqtSignal(int)  # experiment_id
    training_progress = pyqtSignal(int, int, dict)  # experiment_id, step, metrics
    training_completed = pyqtSignal(int, bool)  # experiment_id, success
    
    # Model signals
    model_created = pyqtSignal(int, str)  # model_id, name
    model_deleted = pyqtSignal(int)  # model_id
    
    # Export signals
    export_started = pyqtSignal(int, str)  # export_id, format
    export_completed = pyqtSignal(int, bool)  # export_id, success
    
    # Project signals
    project_created = pyqtSignal(int, str)  # project_id, name
    project_deleted = pyqtSignal(int)  # project_id
    project_changed = pyqtSignal(int)  # project_id
