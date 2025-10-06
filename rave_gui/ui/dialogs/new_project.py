"""
New project creation dialog.
"""
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QFileDialog, 
                              QMessageBox, QDialogButtonBox)
from PyQt6.QtCore import Qt


class NewProjectDialog(QDialog):
    """Dialog for creating a new project."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setMinimumWidth(500)
        self.project_name = ""
        self.project_path = ""
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Project name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Project Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter project name")
        self.name_edit.textChanged.connect(self.validate_input)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Project path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Project Path:"))
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select project directory")
        self.path_edit.textChanged.connect(self.validate_input)
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(button_box)
        
    def browse_path(self):
        """Open file dialog to select project directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Project Directory",
            str(Path.home())
        )
        if path:
            self.path_edit.setText(path)
            
    def validate_input(self):
        """Validate user input and enable/disable OK button."""
        name = self.name_edit.text().strip()
        path = self.path_edit.text().strip()
        
        valid = bool(name and path)
        self.ok_button.setEnabled(valid)
        
    def accept(self):
        """Accept the dialog and store values."""
        self.project_name = self.name_edit.text().strip()
        self.project_path = self.path_edit.text().strip()
        
        # Validate project name (no special characters)
        if not self.project_name.replace(" ", "").replace("_", "").replace("-", "").isalnum():
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Project name can only contain letters, numbers, spaces, hyphens, and underscores."
            )
            return
        
        # Validate path exists or can be created
        try:
            Path(self.project_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Invalid Path",
                f"Cannot create project directory: {e}"
            )
            return
        
        super().accept()
        
    def get_project_data(self):
        """Get the project data entered by user.
        
        Returns:
            Tuple of (name, path)
        """
        return self.project_name, self.project_path
