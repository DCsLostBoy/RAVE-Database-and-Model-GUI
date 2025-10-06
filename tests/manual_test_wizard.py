#!/usr/bin/env python3
"""
Manual test script for the dataset creation wizard.
Run this to visually test the wizard functionality.

Usage:
    python tests/manual_test_wizard.py
"""
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from rave_gui.ui.dialogs.new_dataset import NewDatasetWizard


class TestWindow(QWidget):
    """Simple window to launch the wizard."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dataset Wizard Test")
        self.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout()
        
        btn = QPushButton("Open Dataset Creation Wizard")
        btn.clicked.connect(self.open_wizard)
        layout.addWidget(btn)
        
        self.setLayout(layout)
        
    def open_wizard(self):
        """Open the dataset wizard."""
        wizard = NewDatasetWizard(self)
        wizard.finished.connect(self.on_wizard_finished)
        wizard.show()
        
    def on_wizard_finished(self, result):
        """Handle wizard completion."""
        if result == 1:  # Accepted
            print("Wizard completed successfully!")
            print(f"Audio files: {len(self.sender().get_audio_files())}")
            print(f"Config: {self.sender().get_dataset_config()}")
        else:
            print("Wizard cancelled")


def main():
    """Run the test application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = TestWindow()
    window.show()
    
    print("=" * 60)
    print("Dataset Creation Wizard Manual Test")
    print("=" * 60)
    print("\nClick the button to open the wizard and test:")
    print("1. Intro page navigation")
    print("2. File browsing and drag-and-drop")
    print("3. Audio preview and playback")
    print("4. Parameter configuration and validation")
    print("5. Preprocessing page display")
    print("\nNote: You'll need actual audio files to test playback.")
    print("=" * 60)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
