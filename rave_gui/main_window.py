"""
Main window controller for RAVE GUI.
"""
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                              QStackedWidget, QPushButton, QStatusBar, QLabel,
                              QMenu, QMenuBar)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QAction

from rave_gui.core.signals import AppSignals
from rave_gui.core.database import Database
from rave_gui.core.settings import SettingsManager
from rave_gui.backend.project import ProjectManager
from rave_gui.ui.pages.dashboard import DashboardPage
from rave_gui.ui.pages.datasets import DatasetsPage
from rave_gui.ui.pages.training import TrainingPage
from rave_gui.ui.pages.models import ModelsPage
from rave_gui.ui.pages.export import ExportPage


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation and page routing."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAVE GUI")
        self.setMinimumSize(1200, 800)
        
        # Enable high-DPI scaling
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
        
        # Set initial size (80% of screen)
        screen = self.screen().availableGeometry()
        self.resize(int(screen.width() * 0.8), int(screen.height() * 0.8))
        
        # Get signals singleton
        self.signals = AppSignals()
        
        # Initialize settings
        self.settings_manager = SettingsManager()
        
        # Initialize database and managers
        db_path = Path.home() / ".rave_gui" / "rave_gui.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = Database(db_path)
        self.project_manager = ProjectManager(self.db)
        
        self.current_project_id = None
        
        # Initialize UI
        self.init_ui()
        self.connect_signals()
        
        # Show project selector on startup
        self.show_project_selector()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Create stacked widget for pages
        self.pages = QStackedWidget()
        self.pages.addWidget(DashboardPage())
        self.pages.addWidget(DatasetsPage())
        self.pages.addWidget(TrainingPage(self.db))
        self.pages.addWidget(ModelsPage())
        self.pages.addWidget(ExportPage())
        main_layout.addWidget(self.pages)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def create_sidebar(self):
        """Create the sidebar navigation."""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setObjectName("sidebar")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", 0),
            ("Datasets", 1),
            ("Training", 2),
            ("Models", 3),
            ("Export", 4),
        ]
        
        for label, page_index in nav_buttons:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=page_index: self.switch_page(idx))
            layout.addWidget(btn)
            
            if page_index == 0:
                btn.setChecked(True)
        
        layout.addStretch()
        
        return sidebar
    
    def connect_signals(self):
        """Connect application signals."""
        self.signals.status_message.connect(self.show_status_message)
        
    @pyqtSlot(int)
    def switch_page(self, index):
        """Switch to the specified page."""
        self.pages.setCurrentIndex(index)
        
    @pyqtSlot(str)
    def show_status_message(self, message):
        """Display a status message."""
        self.status_bar.showMessage(message, 5000)
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        new_project_action = QAction("&New Project...", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self.on_new_project)
        file_menu.addAction(new_project_action)
        
        switch_project_action = QAction("&Switch Project...", self)
        switch_project_action.setShortcut("Ctrl+O")
        switch_project_action.triggered.connect(self.show_project_selector)
        file_menu.addAction(switch_project_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        edit_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def on_new_project(self):
        """Handle new project creation."""
        from rave_gui.ui.dialogs.new_project import NewProjectDialog
        from PyQt6.QtWidgets import QMessageBox
        
        dialog = NewProjectDialog(self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            name, path = dialog.get_project_data()
            try:
                project_id = self.project_manager.create_project(name, path)
                self.current_project_id = project_id
                self.update_window_title()
                self.signals.project_created.emit(project_id, name)
                self.signals.status_message.emit(f"Project '{name}' created successfully")
            except ValueError as e:
                QMessageBox.warning(self, "Error", str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create project: {e}")
    
    def show_project_selector(self):
        """Show the project selector dialog."""
        from rave_gui.ui.dialogs.project_selector import ProjectSelectorDialog
        
        dialog = ProjectSelectorDialog(self.project_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            project_id = dialog.get_selected_project_id()
            if project_id:
                self.current_project_id = project_id
                self.update_window_title()
                self.signals.project_changed.emit(project_id)
                
                project = self.project_manager.get_project(project_id)
                if project:
                    self.signals.status_message.emit(f"Switched to project: {project['name']}")
    
    def update_window_title(self):
        """Update window title with current project name."""
        if self.current_project_id:
            project = self.project_manager.get_project(self.current_project_id)
            if project:
                self.setWindowTitle(f"RAVE GUI - {project['name']}")
        else:
            self.setWindowTitle("RAVE GUI")
    
    def show_settings(self):
        """Show settings dialog."""
        from rave_gui.ui.dialogs.settings import SettingsDialog
        
        dialog = SettingsDialog(self.settings_manager, self)
        dialog.theme_changed.connect(self.apply_theme)
        dialog.exec()
    
    def apply_theme(self, theme_name: str):
        """Apply a theme to the application.
        
        Args:
            theme_name: Name of theme ('dark' or 'light')
        """
        from PyQt6.QtWidgets import QApplication
        
        theme_path = Path(__file__).parent / "resources" / "themes" / f"{theme_name}.qss"
        
        if theme_path.exists():
            try:
                with open(theme_path, "r", encoding="utf-8") as f:
                    stylesheet = f.read()
                QApplication.instance().setStyleSheet(stylesheet)
                self.signals.status_message.emit(f"Theme changed to {theme_name}")
            except IOError as e:
                self.signals.status_message.emit(f"Failed to load theme: {e}")
        else:
            self.signals.status_message.emit(f"Theme file not found: {theme_path}")
    
    def show_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "About RAVE GUI",
            "<h3>RAVE GUI v0.1.0</h3>"
            "<p>A graphical interface for RAVE (Realtime Audio Variational autoEncoder)</p>"
            "<p>Developed with PyQt6</p>"
            "<p><a href='https://github.com/acids-ircam/RAVE'>RAVE on GitHub</a></p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Close database connection
        if self.db:
            self.db.close()
        event.accept()
