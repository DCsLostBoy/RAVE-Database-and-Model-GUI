"""
Application entry point for RAVE GUI.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from rave_gui.main_window import MainWindow
from rave_gui.core.settings import SettingsManager


def main():
    """Main entry point for the RAVE GUI application."""
    # Enable high-DPI support before creating QApplication
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        QApplication.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("RAVE GUI")
    app.setOrganizationName("RAVE")
    app.setApplicationVersion("0.1.0")
    
    # Load user's preferred theme
    settings = SettingsManager()
    theme_name = settings.get_theme()
    theme_path = Path(__file__).parent / "resources" / "themes" / f"{theme_name}.qss"
    
    if theme_path.exists():
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except IOError as e:
            print(f"Failed to load theme: {e}")
    else:
        print(f"Theme file not found: {theme_path}")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
