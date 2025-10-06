"""
Application settings dialog.
"""
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QLineEdit, QPushButton, QComboBox, 
                              QDialogButtonBox, QFileDialog)
from PyQt6.QtCore import pyqtSignal


class SettingsDialog(QDialog):
    """Settings dialog for application configuration."""
    
    theme_changed = pyqtSignal(str)  # theme_name
    
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.settings_manager = settings_manager
        self.init_ui()
        self.load_current_settings()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)
        
        # Default paths
        layout.addWidget(QLabel("Default Paths:"))
        
        # Dataset path
        dataset_layout = QHBoxLayout()
        dataset_layout.addWidget(QLabel("Datasets:"))
        self.dataset_path_edit = QLineEdit()
        dataset_layout.addWidget(self.dataset_path_edit)
        browse_dataset_btn = QPushButton("Browse...")
        browse_dataset_btn.clicked.connect(self.browse_dataset_path)
        dataset_layout.addWidget(browse_dataset_btn)
        layout.addLayout(dataset_layout)
        
        # Models path
        models_layout = QHBoxLayout()
        models_layout.addWidget(QLabel("Models:"))
        self.models_path_edit = QLineEdit()
        models_layout.addWidget(self.models_path_edit)
        browse_models_btn = QPushButton("Browse...")
        browse_models_btn.clicked.connect(self.browse_models_path)
        models_layout.addWidget(browse_models_btn)
        layout.addLayout(models_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_current_settings(self):
        """Load current settings into UI."""
        theme = self.settings_manager.get_theme()
        self.theme_combo.setCurrentText(theme.capitalize())
        
        dataset_path = self.settings_manager.get("default_dataset_path", "")
        self.dataset_path_edit.setText(dataset_path)
        
        models_path = self.settings_manager.get("default_models_path", "")
        self.models_path_edit.setText(models_path)
    
    def browse_dataset_path(self):
        """Browse for dataset directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Default Dataset Directory",
            self.dataset_path_edit.text() or str(Path.home())
        )
        if path:
            self.dataset_path_edit.setText(path)
    
    def browse_models_path(self):
        """Browse for models directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Default Models Directory",
            self.models_path_edit.text() or str(Path.home())
        )
        if path:
            self.models_path_edit.setText(path)
    
    def accept(self):
        """Save settings and accept dialog."""
        # Get theme
        theme = self.theme_combo.currentText().lower()
        old_theme = self.settings_manager.get_theme()
        
        # Save all settings
        self.settings_manager.set_theme(theme)
        self.settings_manager.set("default_dataset_path", self.dataset_path_edit.text())
        self.settings_manager.set("default_models_path", self.models_path_edit.text())
        
        # Emit theme changed signal if theme changed
        if theme != old_theme:
            self.theme_changed.emit(theme)
        
        super().accept()
