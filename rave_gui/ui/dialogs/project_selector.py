"""
Project selector dialog.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QListWidget, QListWidgetItem, QPushButton,
                              QMessageBox, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal


class ProjectSelectorDialog(QDialog):
    """Dialog for selecting and managing projects."""
    
    project_selected = pyqtSignal(int)  # project_id
    
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Project")
        self.setMinimumSize(600, 400)
        self.project_manager = project_manager
        self.selected_project_id = None
        self.init_ui()
        self.load_projects()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Select a Project")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Project list
        self.project_list = QListWidget()
        self.project_list.itemDoubleClicked.connect(self.on_project_double_clicked)
        self.project_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.project_list)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        new_btn = QPushButton("New Project...")
        new_btn.clicked.connect(self.on_new_project)
        action_layout.addWidget(new_btn)
        
        delete_btn = QPushButton("Delete Project")
        delete_btn.clicked.connect(self.on_delete_project)
        self.delete_btn = delete_btn
        self.delete_btn.setEnabled(False)
        action_layout.addWidget(delete_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
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
        
    def load_projects(self):
        """Load projects from database."""
        self.project_list.clear()
        projects = self.project_manager.list_projects()
        
        if not projects:
            item = QListWidgetItem("No projects found. Click 'New Project' to create one.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.project_list.addItem(item)
            return
        
        for project in projects:
            item = QListWidgetItem(f"{project['name']} - {project['path']}")
            item.setData(Qt.ItemDataRole.UserRole, project['id'])
            self.project_list.addItem(item)
            
    def on_selection_changed(self):
        """Handle project selection change."""
        items = self.project_list.selectedItems()
        if items:
            item = items[0]
            project_id = item.data(Qt.ItemDataRole.UserRole)
            if project_id is not None:
                self.selected_project_id = project_id
                self.ok_button.setEnabled(True)
                self.delete_btn.setEnabled(True)
            else:
                self.ok_button.setEnabled(False)
                self.delete_btn.setEnabled(False)
        else:
            self.ok_button.setEnabled(False)
            self.delete_btn.setEnabled(False)
            
    def on_project_double_clicked(self, item):
        """Handle double-click on project."""
        project_id = item.data(Qt.ItemDataRole.UserRole)
        if project_id is not None:
            self.selected_project_id = project_id
            self.accept()
            
    def on_new_project(self):
        """Open new project dialog."""
        from rave_gui.ui.dialogs.new_project import NewProjectDialog
        
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, path = dialog.get_project_data()
            try:
                project_id = self.project_manager.create_project(name, path)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Project '{name}' created successfully."
                )
                self.load_projects()
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
                
    def on_delete_project(self):
        """Delete selected project."""
        if self.selected_project_id is None:
            return
        
        project = self.project_manager.get_project(self.selected_project_id)
        if not project:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Project",
            f"Are you sure you want to delete project '{project['name']}'?\n\n"
            "This will only remove the project from the database, not delete files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.project_manager.delete_project(self.selected_project_id)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Project '{project['name']}' deleted successfully."
                )
                self.selected_project_id = None
                self.load_projects()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete project: {e}")
                
    def get_selected_project_id(self):
        """Get the selected project ID.
        
        Returns:
            Selected project ID or None
        """
        return self.selected_project_id
