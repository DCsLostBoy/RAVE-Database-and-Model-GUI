"""
Log viewer widget for displaying real-time training logs.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QTextCursor


class LogViewer(QWidget):
    """Widget for displaying real-time log output."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFontFamily("Consolas")
        layout.addWidget(self.log_text)
        
    def append_log(self, text):
        """Append text to the log viewer."""
        self.log_text.append(text)
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
        
    def clear(self):
        """Clear the log viewer."""
        self.log_text.clear()
