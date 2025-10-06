"""
New training wizard dialog.
"""
from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
                              QLabel, QLineEdit, QComboBox, QSpinBox, 
                              QListWidget, QFormLayout, QTextEdit, QPushButton,
                              QListWidgetItem)
from PyQt6.QtCore import Qt


class NewTrainingWizard(QWizard):
    """Wizard for configuring a new training run."""
    
    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Start New Training")
        self.db = db_connection
        
        # Storage for configuration
        self.config = {}
        
        # Add wizard pages
        self.dataset_page = DatasetSelectionPage(self.db)
        self.config_page = ConfigSelectionPage()
        self.params_page = TrainingParametersPage()
        self.confirmation_page = ConfirmationPage()
        
        self.addPage(self.dataset_page)
        self.addPage(self.config_page)
        self.addPage(self.params_page)
        self.addPage(self.confirmation_page)
        
        # Set wizard style
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        
    def get_config(self) -> dict:
        """Get the complete training configuration.
        
        Returns:
            Configuration dictionary
        """
        config = {}
        
        # Get dataset info
        dataset = self.dataset_page.get_selected_dataset()
        if dataset:
            config['dataset_id'] = dataset['id']
            config['dataset_path'] = dataset['path']
        
        # Get RAVE config
        config['config'] = self.config_page.get_config_name()
        config['overrides'] = self.config_page.get_overrides()
        
        # Get training parameters
        params = self.params_page.get_parameters()
        config.update(params)
        
        return config


class DatasetSelectionPage(QWizardPage):
    """Page for selecting a dataset for training."""
    
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
        self.setTitle("Select Dataset")
        self.setSubTitle("Choose a preprocessed dataset for training.")
        
        layout = QVBoxLayout()
        
        # Dataset list
        self.dataset_list = QListWidget()
        self.dataset_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(QLabel("Available Datasets:"))
        layout.addWidget(self.dataset_list)
        
        # Dataset info display
        info_label = QLabel("Dataset Information:")
        layout.addWidget(info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        layout.addWidget(self.info_text)
        
        self.setLayout(layout)
        self.load_datasets()
        
        # Register field for validation
        self.registerField("dataset_id*", self.dataset_list)
        
    def load_datasets(self):
        """Load datasets from database."""
        datasets = self.db.fetch_all(
            "SELECT * FROM datasets ORDER BY created_at DESC"
        )
        
        for ds in datasets:
            item = QListWidgetItem(ds['name'])
            item.setData(Qt.ItemDataRole.UserRole, ds)
            self.dataset_list.addItem(item)
    
    def on_selection_changed(self):
        """Handle dataset selection change."""
        items = self.dataset_list.selectedItems()
        if items:
            dataset = items[0].data(Qt.ItemDataRole.UserRole)
            info = f"Name: {dataset['name']}\n"
            info += f"Path: {dataset['path']}\n"
            info += f"Samples: {dataset.get('num_samples', 'N/A')}\n"
            info += f"Channels: {dataset.get('channels', 'N/A')}\n"
            info += f"Sample Rate: {dataset.get('sample_rate', 'N/A')} Hz"
            self.info_text.setText(info)
    
    def get_selected_dataset(self):
        """Get the selected dataset."""
        items = self.dataset_list.selectedItems()
        if items:
            return items[0].data(Qt.ItemDataRole.UserRole)
        return None
    
    def isComplete(self):
        """Check if page is complete."""
        return len(self.dataset_list.selectedItems()) > 0


class ConfigSelectionPage(QWizardPage):
    """Page for selecting RAVE model configuration."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Select Model Configuration")
        self.setSubTitle("Choose the RAVE model architecture and configuration.")
        
        layout = QFormLayout()
        
        # Base config selector
        self.config_combo = QComboBox()
        self.config_combo.addItems(['v1', 'v2', 'v3', 'discrete'])
        self.config_combo.setCurrentText('v2')
        layout.addRow("Base Config:", self.config_combo)
        
        # Additional modifiers
        self.modifiers = QListWidget()
        self.modifiers.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.modifiers.addItems(['causal', 'snake', 'noise'])
        layout.addRow("Modifiers (optional):", self.modifiers)
        
        self.setLayout(layout)
    
    def get_config_name(self) -> str:
        """Get the selected config name."""
        return self.config_combo.currentText()
    
    def get_overrides(self) -> list:
        """Get configuration overrides."""
        overrides = []
        # Add modifier configs if selected
        for item in self.modifiers.selectedItems():
            overrides.append(f"--config {item.text()}")
        return overrides


class TrainingParametersPage(QWizardPage):
    """Page for setting training parameters."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Training Parameters")
        self.setSubTitle("Configure training hyperparameters and settings.")
        
        layout = QFormLayout()
        
        # Training run name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("my_training_run")
        self.registerField("name*", self.name_edit)
        layout.addRow("Run Name:", self.name_edit)
        
        # Max steps
        self.max_steps_spin = QSpinBox()
        self.max_steps_spin.setRange(1000, 10000000)
        self.max_steps_spin.setValue(500000)
        self.max_steps_spin.setSingleStep(10000)
        layout.addRow("Max Steps:", self.max_steps_spin)
        
        # Batch size
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 128)
        self.batch_size_spin.setValue(8)
        layout.addRow("Batch Size:", self.batch_size_spin)
        
        # Learning rate
        self.lr_edit = QLineEdit()
        self.lr_edit.setText("1e-4")
        layout.addRow("Learning Rate:", self.lr_edit)
        
        self.setLayout(layout)
    
    def get_parameters(self) -> dict:
        """Get training parameters."""
        return {
            'name': self.name_edit.text(),
            'max_steps': self.max_steps_spin.value(),
            'batch_size': self.batch_size_spin.value(),
            'learning_rate': self.lr_edit.text()
        }


class ConfirmationPage(QWizardPage):
    """Final confirmation page showing all selected options."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Confirm Training Configuration")
        self.setSubTitle("Review your settings before starting training.")
        
        layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)
        
        self.setLayout(layout)
    
    def initializePage(self):
        """Initialize page with summary of all selections."""
        wizard = self.wizard()
        
        summary = "=== Training Configuration Summary ===\n\n"
        
        # Dataset info
        dataset = wizard.dataset_page.get_selected_dataset()
        if dataset:
            summary += f"Dataset: {dataset['name']}\n"
            summary += f"Path: {dataset['path']}\n\n"
        
        # Config info
        summary += f"RAVE Config: {wizard.config_page.get_config_name()}\n"
        overrides = wizard.config_page.get_overrides()
        if overrides:
            summary += f"Modifiers: {', '.join(overrides)}\n\n"
        else:
            summary += "\n"
        
        # Parameters
        params = wizard.params_page.get_parameters()
        summary += f"Run Name: {params['name']}\n"
        summary += f"Max Steps: {params['max_steps']:,}\n"
        summary += f"Batch Size: {params['batch_size']}\n"
        summary += f"Learning Rate: {params['learning_rate']}\n"
        
        self.summary_text.setText(summary)
