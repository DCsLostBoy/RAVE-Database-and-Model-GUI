"""
Example test for main window.
"""
import pytest
from PyQt6.QtWidgets import QApplication
from rave_gui.main_window import MainWindow


@pytest.fixture
def app(qtbot):
    """Create application instance for testing."""
    test_app = QApplication.instance()
    if test_app is None:
        test_app = QApplication([])
    return test_app


def test_main_window_creation(qtbot, app):
    """Test that main window can be created."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    assert window.windowTitle() == "RAVE GUI"
    assert window.isVisible() is False  # Not shown yet


def test_main_window_navigation(qtbot, app):
    """Test navigation between pages."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Test initial page
    assert window.pages.currentIndex() == 0
    
    # Test switching pages
    window.switch_page(1)
    assert window.pages.currentIndex() == 1
