"""
Datasets page - Manage and view audio datasets.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QTableWidget, QLabel, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from rave_gui.ui.dialogs.new_dataset import NewDatasetWizard
from rave_gui.core.signals import AppSignals
from rave_gui.backend.dataset import DatasetManager
from datetime import datetime


class DatasetsPage(QWidget):
    """Datasets page for managing audio datasets."""
    
    def __init__(self, parent=None, db_connection=None):
        super().__init__(parent)
        self.db = db_connection
        self.dataset_manager = DatasetManager(db_connection) if db_connection else None
        self.signals = AppSignals()
        
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Datasets")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        
        new_btn = QPushButton("New Dataset")
        new_btn.clicked.connect(self.create_dataset)
        header.addWidget(new_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_datasets)
        header.addWidget(refresh_btn)
        
        layout.addLayout(header)
        
        # Dataset table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Samples", "Duration", "Channels", 
            "Sample Rate", "Created"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
    def connect_signals(self):
        """Connect to application signals."""
        self.signals.dataset_created.connect(self.on_dataset_created)
        
    def create_dataset(self):
        """Open the new dataset wizard."""
        wizard = NewDatasetWizard(self, self.db)
        wizard.exec()
        
    def load_datasets(self):
        """Load datasets from database."""
        if not self.dataset_manager:
            return
            
        datasets = self.dataset_manager.list_datasets()
        self.table.setRowCount(len(datasets))
        
        for row, dataset in enumerate(datasets):
            # Name
            self.table.setItem(row, 0, QTableWidgetItem(dataset['name']))
            
            # Samples
            samples = dataset.get('num_samples') or 0
            self.table.setItem(row, 1, QTableWidgetItem(str(samples)))
            
            # Duration
            sample_rate = dataset.get('sample_rate', 44100)
            duration = samples / sample_rate if sample_rate > 0 and samples else 0
            duration_str = f"{duration:.2f}s"
            self.table.setItem(row, 2, QTableWidgetItem(duration_str))
            
            # Channels
            channels = dataset.get('channels', 1)
            self.table.setItem(row, 3, QTableWidgetItem(str(channels)))
            
            # Sample Rate
            self.table.setItem(row, 4, QTableWidgetItem(f"{sample_rate} Hz"))
            
            # Created
            created_at = dataset.get('created_at', '')
            if created_at:
                # Format the timestamp
                try:
                    dt = datetime.fromisoformat(created_at)
                    created_str = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    created_str = created_at
            else:
                created_str = "Unknown"
            self.table.setItem(row, 5, QTableWidgetItem(created_str))
            
    def on_dataset_created(self, dataset_id, name):
        """Handle dataset created signal."""
        self.load_datasets()
        self.signals.status_message.emit(f"Dataset '{name}' created successfully")
