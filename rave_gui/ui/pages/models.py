"""
Models page - Browse and manage trained models.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ModelsPage(QWidget):
    """Models page for browsing and managing trained models."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        title = QLabel("Models")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # TODO: Add model widgets
        # - Model list/grid view
        # - Model details panel
        # - Model comparison
        # - Audio testing interface
        
        layout.addStretch()
