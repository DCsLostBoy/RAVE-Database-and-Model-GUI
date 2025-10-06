"""
Configuration editor widget for editing Gin config files.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class ConfigEditor(QWidget):
    """Widget for viewing and editing configuration files."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        self.editor = QTextEdit()
        self.editor.setFontFamily("Consolas")
        layout.addWidget(self.editor)
        
    def load_config(self, config_path):
        """Load a configuration file."""
        # TODO: Load and display config file
        pass
    
    def get_config(self):
        """Get the current config text."""
        return self.editor.toPlainText()
