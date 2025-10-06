"""
Dashboard page - Overview of projects, datasets, and recent activity.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class DashboardPage(QWidget):
    """Main dashboard showing project overview and quick actions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dashboard")
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Placeholder content
        title = QLabel("Dashboard")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # TODO: Add project statistics widgets
        # TODO: Add recent activity feed
        # TODO: Add quick action buttons
    
    def connect_signals(self):
        """Connect signals and slots."""
        # TODO: Connect to AppSignals for updates
        pass
