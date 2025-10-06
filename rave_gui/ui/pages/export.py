"""
Export page - Export models to various formats.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ExportPage(QWidget):
    """Export page for exporting models to different formats."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        title = QLabel("Export")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # TODO: Add export widgets
        # - Model selector
        # - Format options (TorchScript, ONNX)
        # - Export settings
        # - Exported models library
        
        layout.addStretch()
