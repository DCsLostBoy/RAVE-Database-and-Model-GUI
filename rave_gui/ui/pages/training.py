"""
Training page - Configure and monitor model training.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class TrainingPage(QWidget):
    """Training page for configuring and monitoring model training."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        title = QLabel("Training")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # TODO: Add training widgets
        # - Active training runs list
        # - New training button
        # - Training progress displays
        # - Metrics plots
        
        layout.addStretch()
