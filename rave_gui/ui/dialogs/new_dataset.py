"""
New dataset wizard dialog.
"""
from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QLabel,
                              QPushButton, QLineEdit, QSpinBox, QCheckBox)


class NewDatasetWizard(QWizard):
    """Wizard for creating a new dataset."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        
        # Add wizard pages
        self.addPage(IntroPage())
        self.addPage(InputFilesPage())
        self.addPage(ParametersPage())
        self.addPage(PreprocessingPage())


class IntroPage(QWizardPage):
    """Introduction page for the dataset wizard."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Create New Dataset")
        self.setSubTitle("This wizard will help you preprocess audio files for RAVE training.")
        
        layout = QVBoxLayout()
        label = QLabel("A dataset contains preprocessed audio samples ready for training.")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setLayout(layout)


class InputFilesPage(QWizardPage):
    """Page for selecting input audio files."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Select Audio Files")
        self.setSubTitle("Choose the audio files to include in your dataset.")
        
        layout = QVBoxLayout()
        
        self.browse_btn = QPushButton("Browse Folders...")
        self.browse_btn.clicked.connect(self.browse_folders)
        layout.addWidget(self.browse_btn)
        
        # TODO: Add file list widget with audio preview
        
        self.setLayout(layout)
        
    def browse_folders(self):
        """Open folder selection dialog."""
        # TODO: Implement folder browser
        pass


class ParametersPage(QWizardPage):
    """Page for configuring dataset parameters."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Dataset Parameters")
        self.setSubTitle("Configure preprocessing parameters.")
        
        layout = QVBoxLayout()
        
        # Dataset name
        layout.addWidget(QLabel("Dataset Name:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # Sample rate
        layout.addWidget(QLabel("Sample Rate:"))
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(8000, 192000)
        self.sample_rate_spin.setValue(44100)
        layout.addWidget(self.sample_rate_spin)
        
        # Channels
        layout.addWidget(QLabel("Channels:"))
        self.channels_spin = QSpinBox()
        self.channels_spin.setRange(1, 8)
        self.channels_spin.setValue(1)
        layout.addWidget(self.channels_spin)
        
        # Lazy loading option
        self.lazy_check = QCheckBox("Use lazy loading")
        layout.addWidget(self.lazy_check)
        
        layout.addStretch()
        self.setLayout(layout)


class PreprocessingPage(QWizardPage):
    """Page showing preprocessing progress."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Preprocessing")
        self.setSubTitle("Processing audio files...")
        
        layout = QVBoxLayout()
        
        # TODO: Add progress bar and log viewer
        
        self.setLayout(layout)
