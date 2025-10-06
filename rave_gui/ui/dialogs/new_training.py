"""
New training wizard dialog.
"""
from PyQt6.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QLabel


class NewTrainingWizard(QWizard):
    """Wizard for configuring a new training run."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Start New Training")
        
        # TODO: Add wizard pages
        # - Dataset selection
        # - Config selection
        # - Training parameters
        # - Confirmation
        
        self.addPage(DatasetSelectionPage())


class DatasetSelectionPage(QWizardPage):
    """Page for selecting a dataset for training."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Select Dataset")
        self.setSubTitle("Choose a preprocessed dataset for training.")
        
        layout = QVBoxLayout()
        
        # TODO: Add dataset selector widget
        
        self.setLayout(layout)
