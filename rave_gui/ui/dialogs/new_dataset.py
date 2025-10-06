"""
New dataset wizard dialog.
"""
from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QLabel,
                              QPushButton, QLineEdit, QSpinBox, QCheckBox,
                              QFileDialog, QListWidget, QHBoxLayout, QFormLayout,
                              QProgressBar)
from PyQt6.QtCore import Qt
from pathlib import Path
from rave_gui.backend.dataset import DatasetManager
from rave_gui.core.signals import AppSignals
from rave_gui.core.process import ProcessThread, RAVEProcess
from rave_gui.ui.widgets.log_viewer import LogViewer


class NewDatasetWizard(QWizard):
    """Wizard for creating a new dataset."""
    
    def __init__(self, parent=None, db_connection=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        self.db = db_connection
        self.dataset_manager = DatasetManager(db_connection) if db_connection else None
        self.signals = AppSignals()
        
        # Store wizard data
        self.input_path = None
        self.output_path = None
        self.dataset_id = None
        
        # Add wizard pages
        self.intro_page = IntroPage()
        self.input_page = InputFilesPage()
        self.params_page = ParametersPage()
        self.process_page = PreprocessingPage(self)
        
        self.addPage(self.intro_page)
        self.addPage(self.input_page)
        self.addPage(self.params_page)
        self.addPage(self.process_page)
        
    def accept(self):
        """Override accept to emit signals."""
        if self.dataset_id:
            dataset = self.dataset_manager.get_dataset(self.dataset_id)
            if dataset:
                self.signals.dataset_created.emit(self.dataset_id, dataset['name'])
        super().accept()


class IntroPage(QWizardPage):
    """Introduction page for the dataset wizard."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Create New Dataset")
        self.setSubTitle("This wizard will help you preprocess audio files for RAVE training.")
        
        layout = QVBoxLayout()
        
        info_text = QLabel(
            "A dataset contains preprocessed audio samples ready for training.\n\n"
            "The preprocessing step will:\n"
            "• Convert audio files to the specified format\n"
            "• Resample to the target sample rate\n"
            "• Split audio into fixed-length chunks\n"
            "• Store data in an LMDB database for efficient training"
        )
        info_text.setWordWrap(True)
        layout.addWidget(info_text)
        
        layout.addStretch()
        self.setLayout(layout)


class InputFilesPage(QWizardPage):
    """Page for selecting input audio files."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Select Audio Files")
        self.setSubTitle("Choose the folder containing audio files to include in your dataset.")
        
        layout = QVBoxLayout()
        
        # Input path selection
        input_layout = QHBoxLayout()
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setPlaceholderText("Select input folder...")
        self.input_path_edit.setReadOnly(True)
        input_layout.addWidget(self.input_path_edit)
        
        self.browse_input_btn = QPushButton("Browse...")
        self.browse_input_btn.clicked.connect(self.browse_input_folder)
        input_layout.addWidget(self.browse_input_btn)
        
        layout.addWidget(QLabel("Input Folder:"))
        layout.addLayout(input_layout)
        
        # Output path selection
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Select output folder...")
        self.output_path_edit.setReadOnly(True)
        output_layout.addWidget(self.output_path_edit)
        
        self.browse_output_btn = QPushButton("Browse...")
        self.browse_output_btn.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.browse_output_btn)
        
        layout.addWidget(QLabel("\nOutput Folder:"))
        layout.addLayout(output_layout)
        
        # File list
        layout.addWidget(QLabel("\nAudio files will be scanned from the input folder."))
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Register fields for validation
        self.registerField("input_path*", self.input_path_edit)
        self.registerField("output_path*", self.output_path_edit)
        
    def browse_input_folder(self):
        """Open folder selection dialog for input."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Input Folder",
            str(Path.home())
        )
        if folder:
            self.input_path_edit.setText(folder)
            
    def browse_output_folder(self):
        """Open folder selection dialog for output."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            str(Path.home())
        )
        if folder:
            self.output_path_edit.setText(folder)


class ParametersPage(QWizardPage):
    """Page for configuring dataset parameters."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Dataset Parameters")
        self.setSubTitle("Configure preprocessing parameters.")
        
        layout = QFormLayout()
        
        # Dataset name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., my_dataset")
        layout.addRow("Dataset Name*:", self.name_edit)
        
        # Sample rate
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(8000, 192000)
        self.sample_rate_spin.setValue(44100)
        self.sample_rate_spin.setSuffix(" Hz")
        layout.addRow("Sample Rate:", self.sample_rate_spin)
        
        # Channels
        self.channels_spin = QSpinBox()
        self.channels_spin.setRange(1, 8)
        self.channels_spin.setValue(1)
        layout.addRow("Channels:", self.channels_spin)
        
        # Number of samples per chunk
        self.num_signal_spin = QSpinBox()
        self.num_signal_spin.setRange(1024, 262144)
        self.num_signal_spin.setValue(65536)
        self.num_signal_spin.setToolTip("Number of audio samples per chunk")
        layout.addRow("Samples per Chunk:", self.num_signal_spin)
        
        # Lazy loading option
        self.lazy_check = QCheckBox("Use lazy loading (for large datasets)")
        layout.addRow("", self.lazy_check)
        
        self.setLayout(layout)
        
        # Register fields for validation
        self.registerField("dataset_name*", self.name_edit)
        self.registerField("sample_rate", self.sample_rate_spin)
        self.registerField("channels", self.channels_spin)
        self.registerField("num_signal", self.num_signal_spin)
        self.registerField("lazy", self.lazy_check)
        
    def validatePage(self):
        """Validate the page before proceeding."""
        if not self.name_edit.text().strip():
            return False
        return True


class PreprocessingPage(QWizardPage):
    """Page showing preprocessing progress."""
    
    def __init__(self, wizard):
        super().__init__()
        self.wizard_ref = wizard
        self.setTitle("Preprocessing")
        self.setSubTitle("Processing audio files...")
        self.setFinalPage(True)
        
        layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to start preprocessing...")
        layout.addWidget(self.status_label)
        
        # Log viewer
        layout.addWidget(QLabel("\nPreprocessing Log:"))
        self.log_viewer = LogViewer()
        layout.addWidget(self.log_viewer)
        
        self.setLayout(layout)
        
        # Processing thread
        self.process_thread = None
        
    def initializePage(self):
        """Start preprocessing when page is shown."""
        self.start_preprocessing()
        
    def start_preprocessing(self):
        """Start the preprocessing operation."""
        # Create dataset entry in database first
        config = {
            'name': self.field('dataset_name'),
            'path': self.field('output_path'),
            'input_path': self.field('input_path'),
            'channels': self.field('channels'),
            'sample_rate': self.field('sample_rate'),
            'num_samples': None  # Will be updated after preprocessing
        }
        
        try:
            self.wizard_ref.dataset_id = self.wizard_ref.dataset_manager.create_dataset(config)
            self.wizard_ref.output_path = Path(self.field('output_path'))
            
            # Build preprocessing command
            cmd = RAVEProcess.preprocess(
                input_path=Path(self.field('input_path')),
                output_path=self.wizard_ref.output_path,
                sample_rate=self.field('sample_rate'),
                channels=self.field('channels'),
                num_signal=self.field('num_signal'),
                lazy=self.field('lazy')
            )
            
            # Start preprocessing thread
            self.process_thread = ProcessThread(cmd)
            self.process_thread.output.connect(self.on_output)
            self.process_thread.progress.connect(self.on_progress)
            self.process_thread.finished.connect(self.on_finished)
            self.process_thread.start()
            
            self.status_label.setText("Preprocessing started...")
            self.log_viewer.append_log("Starting RAVE preprocessing...")
            self.log_viewer.append_log(f"Command: {' '.join(cmd)}\n")
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.log_viewer.append_log(f"ERROR: {str(e)}")
            
    def on_output(self, text):
        """Handle output from preprocessing."""
        self.log_viewer.append_log(text)
        
    def on_progress(self, percentage, message):
        """Handle progress updates."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        
    def on_finished(self, success, message):
        """Handle preprocessing completion."""
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("Preprocessing completed successfully!")
            self.log_viewer.append_log("\n✓ Preprocessing completed successfully")
        else:
            self.status_label.setText(f"Preprocessing failed: {message}")
            self.log_viewer.append_log(f"\n✗ Preprocessing failed: {message}")
