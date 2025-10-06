# RAVE GUI - Implementation Roadmap

## Quick Start Guide for Development

This document provides a practical roadmap for implementing the RAVE GUI, with concrete steps and recommendations.

---

## Phase 0: Setup & Preparation (Week 0)

### Decision Points

#### 1. Choose GUI Framework

##### Recommendation: PyQt6

**Rationale**:

- Native Python integration (works seamlessly with existing RAVE code)
- Rich widget library (tables, plots, custom controls)
- Cross-platform (Windows, Mac, Linux)
- Excellent documentation and community
- Professional appearance
- Built-in threading support (critical for non-blocking operations)

**Alternatives Considered**:

- ❌ Tkinter: Too basic, limited widgets, dated appearance
- ❌ Electron: Heavier, requires JavaScript/TypeScript, separate backend needed
- ✅ PyQt6: Best balance of features, performance, and Python integration

#### 2. Project Structure

```
rave-gui/
├── rave_gui/                    # Main application package
│   ├── __init__.py
│   ├── app.py                   # Application entry point
│   ├── main_window.py           # Main window controller
│   │
│   ├── ui/                      # UI components
│   │   ├── __init__.py
│   │   ├── pages/               # Main page widgets
│   │   │   ├── dashboard.py
│   │   │   ├── datasets.py
│   │   │   ├── training.py
│   │   │   ├── models.py
│   │   │   └── export.py
│   │   ├── widgets/             # Reusable widgets
│   │   │   ├── audio_player.py
│   │   │   ├── metrics_plot.py
│   │   │   ├── config_editor.py
│   │   │   └── log_viewer.py
│   │   └── dialogs/             # Dialog windows
│   │       ├── new_dataset.py
│   │       ├── new_training.py
│   │       └── settings.py
│   │
│   ├── backend/                 # Business logic
│   │   ├── __init__.py
│   │   ├── project.py           # Project management
│   │   ├── dataset.py           # Dataset operations
│   │   ├── training.py          # Training management
│   │   ├── model.py             # Model operations
│   │   └── export.py            # Export operations
│   │
│   ├── core/                    # Core utilities
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite interface
│   │   ├── process.py           # Subprocess management
│   │   ├── config.py            # Config parsing
│   │   ├── logger.py            # Logging utilities
│   │   └── signals.py           # Qt signals for communication
│   │
│   └── resources/               # Static resources
│       ├── icons/
│       ├── themes/
│       │   ├── dark.qss
│       │   └── light.qss
│       └── templates/
│
├── tests/                       # Test suite
│   ├── test_ui/
│   ├── test_backend/
│   └── test_integration/
│
├── docs/                        # Documentation
│   ├── user_guide.md
│   ├── developer_guide.md
│   └── screenshots/
│
├── requirements.txt             # Python dependencies
├── setup.py                     # Installation script
├── README.md
└── .gitignore
```

#### 3. Development Environment Setup

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install PyQt6 PyQt6-WebEngine
pip install matplotlib numpy scipy
pip install watchdog lmdb pyyaml
pip install sounddevice soundfile librosa
pip install pytest pytest-qt  # For testing
pip install acids-rave  # Existing RAVE

# For development
pip install black flake8 mypy  # Code quality tools
```

---

## Phase 1: MVP - Minimum Viable Product (Weeks 1-4)

**Goal**: Create a working prototype with one complete workflow: dataset preprocessing.

### Week 1: Foundation

**Deliverables**:

- PyQt6 application shell
- Main window with sidebar navigation
- Basic page routing
- Application settings persistence

**Code Example - Main Application**:

```python
# rave_gui/app.py
import sys
from PyQt6.QtWidgets import QApplication
from rave_gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RAVE GUI")
    
    # Load stylesheet
    with open("resources/themes/dark.qss", "r") as f:
        app.setStyleSheet(f.read())
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

**Tasks**:

1. Set up project structure
2. Create main window with QStackedWidget for pages
3. Implement sidebar navigation with icons
4. Add status bar for notifications
5. Create settings dialog (theme, paths)
6. Implement basic error handling

### Week 2: Dataset Management UI

**Deliverables**:

- Dataset creation wizard
- File browser with audio preview
- Parameter configuration form
- Preprocessing progress display

**Code Example - Dataset Wizard**:

```python
# rave_gui/ui/dialogs/new_dataset.py
from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout,
                              QLabel, QLineEdit, QFileDialog, QPushButton)

class NewDatasetWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        
        # Add pages
        self.addPage(IntroPage())
        self.addPage(InputFilesPage())
        self.addPage(ParametersPage())
        self.addPage(PreprocessingPage())
        
class InputFilesPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Select Audio Files")
        layout = QVBoxLayout()
        
        # File browser button
        self.browse_btn = QPushButton("Browse Folders...")
        self.browse_btn.clicked.connect(self.browse_folders)
        layout.addWidget(self.browse_btn)
        
        # File list widget with preview
        self.file_list = AudioFileList()
        layout.addWidget(self.file_list)
        
        self.setLayout(layout)
```

**Tasks**:

1. Create wizard flow (intro → files → params → process)
2. Build file browser with drag-and-drop
3. Add audio preview player
4. Create parameter form (channels, sample rate, etc.)
5. Implement form validation
6. Add folder selection dialog

### Week 3: Dataset Processing Backend

**Deliverables**:

- Subprocess wrapper for `rave preprocess`
- Progress monitoring
- Log parsing and display
- Error handling

**Code Example - Process Manager**:

```python
# rave_gui/backend/dataset.py
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

class PreprocessThread(QThread):
    progress = pyqtSignal(int, str)  # percentage, message
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
    def run(self):
        cmd = [
            "rave", "preprocess",
            "--input_path", self.config['input_path'],
            "--output_path", self.config['output_path'],
            "--channels", str(self.config['channels']),
            "--sampling_rate", str(self.config['sample_rate'])
        ]
        
        if self.config.get('lazy'):
            cmd.append("--lazy")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            # Parse progress from output
            progress, msg = self.parse_progress(line)
            self.progress.emit(progress, msg)
        
        success = process.wait() == 0
        self.finished.emit(success, "Complete" if success else "Failed")
```

**Tasks**:

1. Create subprocess wrapper
2. Implement progress monitoring
3. Parse preprocessing output
4. Add cancellation support
5. Implement error recovery
6. Create completion notification

### Week 4: Dataset Library & Polish

**Deliverables**:

- Dataset list view
- Dataset metadata display
- Search and filtering
- Database integration

**Code Example - Dataset List**:

```python
# rave_gui/ui/pages/datasets.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton)

class DatasetsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        new_btn = QPushButton("New Dataset")
        new_btn.clicked.connect(self.create_dataset)
        toolbar.addWidget(new_btn)
        layout.addLayout(toolbar)
        
        # Dataset table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Samples", "Duration", "Channels", 
            "Sample Rate", "Created"
        ])
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_datasets()
    
    def load_datasets(self):
        # Load from database
        datasets = self.db.get_all_datasets()
        self.table.setRowCount(len(datasets))
        
        for i, ds in enumerate(datasets):
            self.table.setItem(i, 0, QTableWidgetItem(ds.name))
            # ... populate other columns
```

**Tasks**:

1. Create SQLite database schema
2. Implement dataset CRUD operations
3. Build dataset list widget
4. Add search and filtering
5. Implement dataset deletion with confirmation
6. Add dataset details view

**MVP Milestone**: At the end of Phase 1, users should be able to:

- ✅ Launch the GUI
- ✅ Create a new dataset through the wizard
- ✅ Monitor preprocessing progress
- ✅ See completed datasets in the library
- ✅ View dataset details

---

## Phase 2: Core Training (Weeks 5-10)

### Week 5-6: Training Configuration

**Deliverables**:

- Training wizard
- Config file browser
- Parameter forms
- Configuration validation

**Key Features**:

- Dataset selector (dropdown with all available datasets)
- Model config selector (v1, v2, v3, discrete, etc.)
- Config composition (add causal, snake, augmentations)
- Training parameters (steps, validation frequency, batch size)
- GPU selection
- Memory estimation

**Tasks**:

1. Parse all Gin config files
2. Create config selector UI
3. Build parameter forms with validation
4. Implement config preview/composition
5. Add memory usage estimator
6. Create training templates

### Week 7-8: Training Execution & Monitoring

**Deliverables**:

- Training process launcher
- Real-time log viewer
- Live metrics parsing
- Training control (stop/pause)

**Key Features**:

- Launch training in subprocess
- Monitor training logs in real-time
- Parse and display metrics (loss, learning rate)
- Plot live training curves
- Show GPU/CPU/RAM usage
- Add stop/pause controls

**Technical Challenge**: Real-time log parsing without blocking UI

**Solution**:

```python
# rave_gui/core/log_monitor.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt6.QtCore import QObject, pyqtSignal

class LogMonitor(QObject, FileSystemEventHandler):
    new_metrics = pyqtSignal(dict)
    
    def __init__(self, log_path):
        super().__init__()
        self.log_path = log_path
        self.observer = Observer()
        
    def start(self):
        self.observer.schedule(self, str(self.log_path.parent))
        self.observer.start()
    
    def on_modified(self, event):
        if event.src_path == str(self.log_path):
            # Parse new lines
            metrics = self.parse_new_lines()
            if metrics:
                self.new_metrics.emit(metrics)
```

**Tasks**:

1. Create training subprocess wrapper
2. Implement log file monitoring
3. Parse PyTorch Lightning logs
4. Create metrics plotting widget
5. Add system resource monitoring
6. Implement training control signals

### Week 9-10: Experiment Tracking

**Deliverables**:

- Experiments database
- Experiments list view
- Experiment comparison
- TensorBoard integration

**Tasks**:

1. Design experiments database schema
2. Track all training runs automatically
3. Create experiments table view
4. Build comparison interface
5. Add TensorBoard launcher
6. Implement experiment notes/tagging

---

## Phase 3: Model Management (Weeks 11-14)

### Week 11-12: Model Library

**Deliverables**:

- Model list view
- Model metadata display
- Model search/filtering
- Checkpoint browser

**Tasks**:

1. Scan and index trained models
2. Create model list widget
3. Display model details
4. Show training curves
5. Add model comparison
6. Implement model organization

### Week 13-14: Model Testing

**Deliverables**:

- Audio upload and testing
- Side-by-side comparison
- Waveform/spectrogram visualization
- Evaluation metrics

**Tasks**:

1. Create audio upload widget
2. Implement model inference
3. Build audio comparison player
4. Add waveform visualization
5. Implement spectrogram viewer
6. Calculate evaluation metrics (PESQ, STOI)

---

## Phase 4: Export & Polish (Weeks 15-18)

### Week 15-16: Export System

**Deliverables**:

- Export wizard
- Format selection
- Export validation
- Exported models library

**Tasks**:

1. Create export wizard
2. Implement TorchScript export
3. Implement ONNX export
4. Add export validation
5. Create export presets
6. Build exported models library

### Week 17-18: Testing & Bug Fixes

**Focus**:

- Integration testing
- Bug fixing
- Performance optimization
- Documentation

---

## Quick Win Features (Implement Early)

These features provide immediate value and help with testing:

1. **Dark Mode**: Visual appeal, reduces eye strain
2. **Keyboard Shortcuts**: Power user efficiency
3. **Drag & Drop**: Intuitive file selection
4. **Audio Preview**: Essential for dataset work
5. **Real-time Progress**: Shows the app is working
6. **Recent Projects**: Quick access to ongoing work

---

## Technical Best Practices

### 1. Threading Model

**Rule**: Never block the UI thread

```python
# WRONG - Blocks UI
def train_model(self):
    subprocess.run(["rave", "train", ...])  # UI freezes!
    
# RIGHT - Use QThread
def train_model(self):
    self.train_thread = TrainingThread(config)
    self.train_thread.progress.connect(self.update_progress)
    self.train_thread.finished.connect(self.on_training_finished)
    self.train_thread.start()
```

### 2. Signal-Slot Pattern

**Use Qt signals for all cross-component communication**:

```python
# rave_gui/core/signals.py
from PyQt6.QtCore import QObject, pyqtSignal

class AppSignals(QObject):
    dataset_created = pyqtSignal(str)  # dataset_name
    training_started = pyqtSignal(str)  # run_name
    training_progress = pyqtSignal(int, dict)  # step, metrics
    model_exported = pyqtSignal(str)  # model_path
```

### 3. Database Design

```sql
-- projects.db schema
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    created_at TIMESTAMP
);

CREATE TABLE datasets (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    num_samples INTEGER,
    channels INTEGER,
    sample_rate INTEGER,
    created_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE experiments (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    name TEXT NOT NULL,
    dataset_id INTEGER,
    config TEXT,  -- JSON
    status TEXT,  -- 'running', 'completed', 'failed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metrics TEXT,  -- JSON
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);
```

### 4. Error Handling

**Always handle errors gracefully**:

```python
from PyQt6.QtWidgets import QMessageBox

def safe_operation(self):
    try:
        # Risky operation
        result = do_something()
    except FileNotFoundError as e:
        QMessageBox.critical(
            self,
            "File Not Found",
            f"Could not find file: {e.filename}\n"
            "Please check your dataset path."
        )
    except subprocess.CalledProcessError as e:
        QMessageBox.critical(
            self,
            "Process Error",
            f"Training failed:\n{e.stderr}\n"
            "Check logs for details."
        )
    except Exception as e:
        QMessageBox.critical(
            self,
            "Unexpected Error",
            f"An error occurred: {str(e)}\n"
            "Please report this issue."
        )
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_backend/test_dataset.py
import pytest
from rave_gui.backend.dataset import DatasetManager

def test_dataset_creation():
    dm = DatasetManager()
    config = {
        'name': 'test_dataset',
        'input_path': '/audio',
        'output_path': '/output',
        'channels': 1,
        'sample_rate': 44100
    }
    result = dm.create_dataset(config)
    assert result.success
    assert result.dataset_id is not None
```

### Integration Tests

```python
# tests/test_integration/test_workflow.py
def test_full_workflow(qtbot):
    # Test complete dataset → train → export workflow
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Create dataset
    # ... interact with wizard
    
    # Start training
    # ... configure and launch
    
    # Export model
    # ... test export
```

---

## Documentation Plan

### User Documentation

1. **Getting Started Guide**: First 10 minutes with the app
2. **User Manual**: Complete feature reference
3. **Tutorials**: Video walkthroughs
4. **FAQ**: Common questions and issues
5. **Troubleshooting**: Error messages and solutions

### Developer Documentation

1. **Architecture Overview**: System design
2. **API Reference**: Internal APIs
3. **Contributing Guide**: How to contribute
4. **Plugin Development**: Extending the app

---

## Performance Targets

- **UI Responsiveness**: < 100ms for all interactions
- **Application Startup**: < 3 seconds
- **Dataset Loading**: < 1 second for 1000 samples
- **Training Start**: < 30 seconds from config to running
- **Metrics Update**: < 1 second latency from log to display
- **Memory Usage**: < 500 MB idle, < 2 GB during training monitoring

---

## Release Checklist

### Before Alpha Release

- [ ] Core workflows functional
- [ ] No critical bugs
- [ ] Basic error handling
- [ ] Minimal documentation

### Before Beta Release

- [ ] All planned features implemented
- [ ] Comprehensive error handling
- [ ] Performance optimized
- [ ] User guide complete
- [ ] Community testing completed

### Before v1.0 Release

- [ ] Zero critical bugs
- [ ] All features polished
- [ ] Complete documentation
- [ ] Accessibility tested
- [ ] Cross-platform verified
- [ ] Installation packages created
- [ ] Marketing materials ready

---

## Resources & References

### PyQt6 Learning

- [Official PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Qt for Python Documentation](https://doc.qt.io/qtforpython/)
- [Python GUI Programming with PyQt6](https://realpython.com/python-pyqt-gui-calculator/)

### Audio Processing

- [librosa Documentation](https://librosa.org/doc/latest/)
- [sounddevice Documentation](https://python-sounddevice.readthedocs.io/)

### Design Inspiration

- Ableton Live (DAW UI/UX)
- TensorBoard (metrics visualization)
- DaVinci Resolve (project management)
- GitHub Desktop (git interface simplification)

---

## Next Steps

1. **Set up development environment** (Day 1)
2. **Create project structure** (Day 1)
3. **Build minimal main window** (Day 2-3)
4. **Implement first wizard (dataset creation)** (Week 1-2)
5. **Test with real audio files** (Week 2)
6. **Iterate based on feedback** (Ongoing)

**Remember**: Start simple, get it working, then make it beautiful. Focus on one complete workflow before adding breadth. Test early and often with real users.
