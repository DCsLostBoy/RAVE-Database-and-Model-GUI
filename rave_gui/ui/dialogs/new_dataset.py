"""
New dataset wizard dialog.
"""
from pathlib import Path
from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QSpinBox, QCheckBox, QFileDialog,
                              QListWidget, QListWidgetItem, QProgressBar, QTextEdit,
                              QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from rave_gui.ui.widgets.audio_player import AudioPlayer


class NewDatasetWizard(QWizard):
    """Wizard for creating a new dataset."""
    
    # Signals
    preprocessing_started = pyqtSignal(dict)  # Emits config dict
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(800, 600)
        
        # Store shared data
        self.audio_files = []
        self.dataset_config = {}
        
        # Add wizard pages
        self.intro_page = IntroPage()
        self.files_page = InputFilesPage()
        self.params_page = ParametersPage()
        self.process_page = PreprocessingPage()
        
        self.addPage(self.intro_page)
        self.addPage(self.files_page)
        self.addPage(self.params_page)
        self.addPage(self.process_page)
        
    def get_audio_files(self):
        """Get list of selected audio files."""
        return self.files_page.get_audio_files()
        
    def get_dataset_config(self):
        """Get dataset configuration parameters."""
        return self.params_page.get_config()


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
    
    # Supported audio formats
    AUDIO_EXTENSIONS = ['.wav', '.mp3', '.flac', '.ogg', '.aif', '.aiff', '.opus', '.aac']
    
    def __init__(self):
        super().__init__()
        self.setTitle("Select Audio Files")
        self.setSubTitle("Choose the audio files to include in your dataset. You can drag and drop folders or use the browse button.")
        
        self.audio_files = []
        self.init_ui()
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Browse buttons
        btn_layout = QHBoxLayout()
        self.browse_folder_btn = QPushButton("Browse Folders...")
        self.browse_folder_btn.clicked.connect(self.browse_folders)
        btn_layout.addWidget(self.browse_folder_btn)
        
        self.browse_files_btn = QPushButton("Add Files...")
        self.browse_files_btn.clicked.connect(self.browse_files)
        btn_layout.addWidget(self.browse_files_btn)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_files)
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # File list
        list_label = QLabel("Audio Files:")
        layout.addWidget(list_label)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.file_list.currentItemChanged.connect(self.on_file_selected)
        layout.addWidget(self.file_list)
        
        # File count label
        self.count_label = QLabel("0 files selected")
        self.count_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.count_label)
        
        # Audio preview
        preview_label = QLabel("Preview:")
        layout.addWidget(preview_label)
        
        self.audio_player = AudioPlayer()
        layout.addWidget(self.audio_player)
        
        self.setLayout(layout)
        
    def browse_folders(self):
        """Open folder selection dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Audio Folder",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.add_files_from_folder(folder)
            
    def browse_files(self):
        """Open file selection dialog."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.wav *.mp3 *.flac *.ogg *.aif *.aiff *.opus *.aac);;All Files (*)"
        )
        
        if files:
            for file in files:
                self.add_audio_file(file)
                
    def add_files_from_folder(self, folder_path):
        """Recursively add all audio files from a folder."""
        folder = Path(folder_path)
        if not folder.exists():
            return
            
        # Find all audio files
        audio_files = []
        for ext in self.AUDIO_EXTENSIONS:
            audio_files.extend(folder.rglob(f'*{ext}'))
            audio_files.extend(folder.rglob(f'*{ext.upper()}'))
            
        # Add unique files
        for file in audio_files:
            self.add_audio_file(str(file))
            
    def add_audio_file(self, file_path):
        """Add an audio file to the list."""
        file_path = Path(file_path)
        
        # Check if already in list
        if str(file_path) in self.audio_files:
            return
            
        # Verify it's an audio file
        if file_path.suffix.lower() not in self.AUDIO_EXTENSIONS:
            return
            
        self.audio_files.append(str(file_path))
        
        # Add to list widget
        item = QListWidgetItem(file_path.name)
        item.setData(Qt.ItemDataRole.UserRole, str(file_path))
        item.setToolTip(str(file_path))
        self.file_list.addItem(item)
        
        self.update_count()
        self.completeChanged.emit()
        
    def clear_files(self):
        """Clear all files from the list."""
        self.audio_files.clear()
        self.file_list.clear()
        self.update_count()
        self.audio_player.stop_playback()
        self.completeChanged.emit()
        
    def update_count(self):
        """Update the file count label."""
        count = len(self.audio_files)
        self.count_label.setText(f"{count} file{'s' if count != 1 else ''} selected")
        
    def on_file_selected(self, current, previous):
        """Handle file selection in the list."""
        if current is None:
            return
            
        file_path = current.data(Qt.ItemDataRole.UserRole)
        self.audio_player.load_audio(file_path)
        
    def get_audio_files(self):
        """Get the list of selected audio files."""
        return self.audio_files.copy()
        
    def isComplete(self):
        """Check if page is complete (at least one file selected)."""
        return len(self.audio_files) > 0
        
    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        """Handle drop event."""
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            
            if path.is_dir():
                self.add_files_from_folder(str(path))
            elif path.is_file() and path.suffix.lower() in self.AUDIO_EXTENSIONS:
                self.add_audio_file(str(path))
                
        event.acceptProposedAction()


class ParametersPage(QWizardPage):
    """Page for configuring dataset parameters."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Dataset Parameters")
        self.setSubTitle("Configure preprocessing parameters for your dataset.")
        
        self.init_ui()
        
        # Register fields for validation
        self.registerField("dataset_name*", self.name_edit)
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Dataset name (required)
        name_label = QLabel("Dataset Name: *")
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter a unique name for this dataset")
        self.name_edit.textChanged.connect(self.on_name_changed)
        layout.addWidget(self.name_edit)
        
        self.name_error_label = QLabel("")
        self.name_error_label.setStyleSheet("color: red; font-size: 10px;")
        layout.addWidget(self.name_error_label)
        
        layout.addSpacing(10)
        
        # Output path
        layout.addWidget(QLabel("Output Path:"))
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Select where to save the preprocessed dataset")
        output_layout.addWidget(self.output_path_edit)
        
        self.browse_output_btn = QPushButton("Browse...")
        self.browse_output_btn.clicked.connect(self.browse_output_path)
        output_layout.addWidget(self.browse_output_btn)
        layout.addLayout(output_layout)
        
        layout.addSpacing(10)
        
        # Sample rate
        layout.addWidget(QLabel("Sample Rate (Hz):"))
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(8000, 192000)
        self.sample_rate_spin.setSingleStep(100)
        self.sample_rate_spin.setValue(44100)
        self.sample_rate_spin.setToolTip("Audio sampling rate for preprocessing")
        layout.addWidget(self.sample_rate_spin)
        
        layout.addSpacing(10)
        
        # Channels
        layout.addWidget(QLabel("Channels:"))
        self.channels_spin = QSpinBox()
        self.channels_spin.setRange(1, 8)
        self.channels_spin.setValue(1)
        self.channels_spin.setToolTip("Number of audio channels (1=mono, 2=stereo)")
        layout.addWidget(self.channels_spin)
        
        layout.addSpacing(10)
        
        # Signal length
        layout.addWidget(QLabel("Signal Length (samples):"))
        self.signal_length_spin = QSpinBox()
        self.signal_length_spin.setRange(1024, 1048576)
        self.signal_length_spin.setSingleStep(1024)
        self.signal_length_spin.setValue(65536)
        self.signal_length_spin.setToolTip("Length of each audio sample in the dataset")
        layout.addWidget(self.signal_length_spin)
        
        layout.addSpacing(10)
        
        # Options
        options_label = QLabel("Options:")
        options_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(options_label)
        
        self.lazy_check = QCheckBox("Use lazy loading")
        self.lazy_check.setToolTip("Load and decode audio on-the-fly instead of preprocessing")
        layout.addWidget(self.lazy_check)
        
        self.dyndb_check = QCheckBox("Dynamic database growth")
        self.dyndb_check.setChecked(True)
        self.dyndb_check.setToolTip("Allow the database to grow dynamically")
        layout.addWidget(self.dyndb_check)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def browse_output_path(self):
        """Open dialog to select output path."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.output_path_edit.setText(folder)
            
    def on_name_changed(self, text):
        """Validate dataset name as user types."""
        if not text:
            self.name_error_label.setText("Dataset name is required")
        elif not text.replace('_', '').replace('-', '').isalnum():
            self.name_error_label.setText("Use only letters, numbers, hyphens, and underscores")
        else:
            self.name_error_label.setText("")
            
        self.completeChanged.emit()
        
    def validatePage(self):
        """Validate the page before proceeding."""
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a dataset name.")
            return False
            
        if not name.replace('_', '').replace('-', '').isalnum():
            QMessageBox.warning(
                self, 
                "Validation Error", 
                "Dataset name should contain only letters, numbers, hyphens, and underscores."
            )
            return False
            
        if not self.output_path_edit.text():
            QMessageBox.warning(self, "Validation Error", "Please select an output path.")
            return False
            
        output_path = Path(self.output_path_edit.text())
        if not output_path.exists():
            reply = QMessageBox.question(
                self,
                "Create Directory?",
                f"The output directory does not exist:\n{output_path}\n\nCreate it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return False
                
        return True
        
    def isComplete(self):
        """Check if page is complete."""
        name = self.name_edit.text().strip()
        has_output = bool(self.output_path_edit.text())
        is_valid_name = name and name.replace('_', '').replace('-', '').isalnum()
        return is_valid_name and has_output
        
    def get_config(self):
        """Get the configuration dictionary."""
        return {
            'name': self.name_edit.text().strip(),
            'output_path': self.output_path_edit.text(),
            'sample_rate': self.sample_rate_spin.value(),
            'channels': self.channels_spin.value(),
            'signal_length': self.signal_length_spin.value(),
            'lazy': self.lazy_check.isChecked(),
            'dyndb': self.dyndb_check.isChecked()
        }


class PreprocessingPage(QWizardPage):
    """Page showing preprocessing progress."""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Preprocessing")
        self.setSubTitle("Processing audio files into dataset format...")
        
        self.is_processing = False
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Ready to start preprocessing")
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label)
        
        layout.addSpacing(10)
        
        # Progress bar
        progress_label = QLabel("Progress:")
        layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        layout.addSpacing(10)
        
        # File counter
        self.file_counter_label = QLabel("Files processed: 0 / 0")
        self.file_counter_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.file_counter_label)
        
        layout.addSpacing(10)
        
        # Log viewer
        log_label = QLabel("Processing Log:")
        layout.addWidget(log_label)
        
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setMaximumHeight(200)
        self.log_viewer.setStyleSheet(
            "background-color: #f5f5f5; font-family: monospace; font-size: 10px;"
        )
        layout.addWidget(self.log_viewer)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_preprocessing)
        btn_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_preprocessing)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def initializePage(self):
        """Called when page is shown."""
        # Get configuration from wizard
        wizard = self.wizard()
        if wizard:
            files = wizard.get_audio_files()
            self.file_counter_label.setText(f"Files to process: {len(files)}")
            self.log_append(f"Dataset configuration loaded")
            self.log_append(f"Audio files selected: {len(files)}")
            
    def start_preprocessing(self):
        """Start the preprocessing process."""
        self.is_processing = True
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.status_label.setText("Processing...")
        
        self.log_append("Starting preprocessing...")
        
        # Get wizard data
        wizard = self.wizard()
        if wizard:
            config = wizard.get_dataset_config()
            files = wizard.get_audio_files()
            
            self.log_append(f"Dataset name: {config.get('name', 'N/A')}")
            self.log_append(f"Output path: {config.get('output_path', 'N/A')}")
            self.log_append(f"Sample rate: {config.get('sample_rate', 'N/A')} Hz")
            self.log_append(f"Channels: {config.get('channels', 'N/A')}")
            self.log_append(f"Signal length: {config.get('signal_length', 'N/A')} samples")
            self.log_append(f"Total files: {len(files)}")
            
            # TODO: Connect to actual preprocessing backend
            # For now, simulate progress
            self.simulate_progress()
            
    def cancel_preprocessing(self):
        """Cancel the preprocessing process."""
        self.log_append("Cancelling preprocessing...")
        self.is_processing = False
        self.cancel_btn.setEnabled(False)
        self.start_btn.setEnabled(True)
        self.status_label.setText("Cancelled")
        
    def simulate_progress(self):
        """Simulate preprocessing progress (for testing)."""
        # This is a placeholder - actual implementation would connect to backend
        for i in range(0, 101, 10):
            self.update_progress(i, i, 100)
            
        self.log_append("Preprocessing completed!")
        self.status_label.setText("Completed")
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.is_processing = False
        self.completeChanged.emit()
        
    def update_progress(self, percent, current, total):
        """Update progress indicators."""
        self.progress_bar.setValue(percent)
        self.file_counter_label.setText(f"Files processed: {current} / {total}")
        
    def log_append(self, message):
        """Append a message to the log viewer."""
        self.log_viewer.append(message)
        
    def isComplete(self):
        """Check if preprocessing is complete."""
        # Page is complete when processing is done (not in progress)
        return not self.is_processing
