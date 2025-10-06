# RAVE GUI - Technical Decisions & Architecture

## Executive Summary

This document explains key technical decisions for the RAVE GUI project and provides architectural guidance.

---

## Technology Stack

### Core Framework: PyQt6

**Decision**: Use PyQt6 as the GUI framework

**Rationale**:

- **Native Python**: Seamless integration with existing RAVE codebase
- **Rich Widgets**: Professional UI components (tables, plots, custom widgets)
- **Performance**: Native performance, handles real-time updates well
- **Cross-platform**: Windows, macOS, Linux support
- **Threading**: Built-in QThread for non-blocking operations
- **Signals/Slots**: Clean event-driven architecture
- **Mature Ecosystem**: 20+ years of development, extensive documentation
- **Commercial Use**: LGPL license suitable for open-source

**Alternatives Considered**:

| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **Tkinter** | Built-in, simple | Limited widgets, dated UI | ❌ Too basic |
| **PyQt6** | Rich features, native | Learning curve | ✅ **Selected** |
| **Electron** | Modern web tech | Large bundle, separate backend | ❌ Overkill |
| **Kivy** | Touch-friendly | Limited desktop features | ❌ Wrong focus |
| **wxPython** | Native widgets | Less polished | ❌ PyQt6 better |

---

## Architecture Pattern: MVC-inspired

### Model-View-Controller Separation

```bash
┌─────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                      │
│  (PyQt6 Widgets, Pages, Dialogs)                             │
│  - main_window.py                                            │
│  - ui/pages/*.py                                             │
│  - ui/widgets/*.py                                           │
│  - ui/dialogs/*.py                                           │
└──────────────────┬──────────────────────────────────────────┘
                   │ Qt Signals/Slots
┌──────────────────▼──────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                    │
│  (Python Classes, No Qt Dependencies)                        │
│  - backend/dataset.py                                        │
│  - backend/training.py                                       │
│  - backend/model.py                                          │
│  - backend/export.py                                         │
└──────────────────┬──────────────────────────────────────────┘
                   │ Function Calls
┌──────────────────▼──────────────────────────────────────────┐
│                      DATA LAYER                              │
│  - core/database.py (SQLite)                                 │
│  - core/process.py (Subprocess management)                   │
│  - Existing RAVE CLI (via subprocess)                        │
│  - File system (datasets, models, configs)                   │
└─────────────────────────────────────────────────────────────┘

**Benefits**:

- **Testability**: Business logic isolated from UI
- **Maintainability**: Clear separation of concerns
- **Reusability**: Backend can be used without UI
- **Flexibility**: UI can be changed without touching logic

---

## Key Architectural Decisions

### 1. CLI Wrapper Approach

**Decision**: Wrap existing RAVE CLI via subprocess, don't import directly

**Rationale**:

- **Isolation**: Training process runs independently
- **Monitoring**: Can monitor logs, resource usage
- **Control**: Can stop/pause/resume training
- **Stability**: UI doesn't crash if training crashes
- **Compatibility**: Works with any RAVE version

**Implementation**:

```python
# backend/training.py
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

class TrainingProcess(QThread):
    stdout = pyqtSignal(str)
    progress = pyqtSignal(int, dict)
    
    def run(self):
        cmd = ["rave", "train", "--config", "v2", ...]
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in self.process.stdout:
            self.stdout.emit(line)
            metrics = self.parse_metrics(line)
            if metrics:
                self.progress.emit(self.step, metrics)
```

### 2. SQLite for Metadata

**Decision**: Use SQLite for tracking projects, datasets, experiments

**Rationale**:

- **Embedded**: No separate database server
- **Portable**: Single file database
- **Fast**: More than sufficient for metadata
- **Reliable**: ACID transactions
- **Built-in**: Python sqlite3 module

**Schema**:

```sql
-- Core entities
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    num_samples INTEGER,
    duration_seconds REAL,
    channels INTEGER,
    sample_rate INTEGER,
    file_format TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    dataset_id INTEGER NOT NULL,
    config_json TEXT NOT NULL,  -- Full configuration as JSON
    status TEXT DEFAULT 'pending',  -- pending, running, completed, failed, stopped
    output_path TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    final_metrics_json TEXT,  -- Final metrics as JSON
    notes TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
);

CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id INTEGER NOT NULL,
    checkpoint_path TEXT NOT NULL,
    checkpoint_step INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_best BOOLEAN DEFAULT 0,
    FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
);

CREATE TABLE exports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    format TEXT NOT NULL,  -- torchscript, onnx
    export_path TEXT NOT NULL,
    streaming BOOLEAN DEFAULT 0,
    prior_model_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_datasets_project ON datasets(project_id);
CREATE INDEX idx_experiments_project ON experiments(project_id);
CREATE INDEX idx_experiments_status ON experiments(status);
CREATE INDEX idx_models_experiment ON models(experiment_id);
```

### 3. Threading Model

**Decision**: Use QThread for all long-running operations

**Rationale**:

- **Responsive UI**: Never block the main thread
- **Progress Updates**: Can emit signals for progress
- **Cancellation**: Can stop operations gracefully
- **Qt Integration**: Works seamlessly with Qt event loop

**Pattern**:

```python
# Always follow this pattern for long operations

# 1. Create QThread subclass
class LongOperation(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def run(self):
        # Do work here
        for i in range(100):
            # Work...
            self.progress.emit(i)
        self.finished.emit(True, "Success")

# 2. Connect signals in UI
def start_operation(self):
    self.thread = LongOperation()
    self.thread.progress.connect(self.update_progress)
    self.thread.finished.connect(self.on_finished)
    self.thread.start()
    
# 3. Update UI via slots
def update_progress(self, value):
    self.progress_bar.setValue(value)
```

### 4. Configuration Management

**Decision**: Parse Gin configs, but store as JSON in database

**Rationale**:

- **Flexibility**: Can modify configs via GUI
- **Portability**: JSON is universal
- **History**: Can track configuration changes
- **Comparison**: Easy to compare different configs

**Implementation**:

```python
# core/config.py
import gin
import json

class ConfigManager:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "rave" / "configs"
        self.configs = self.scan_configs()
    
    def scan_configs(self) -> Dict[str, Path]:
        """Find all .gin files"""
        configs = {}
        for gin_file in self.base_path.rglob("*.gin"):
            name = gin_file.stem
            configs[name] = gin_file
        return configs
    
    def parse_config(self, config_names: List[str]) -> dict:
        """Parse Gin configs and return as dict"""
        gin.clear_config()
        config_files = [self.configs[name] for name in config_names]
        gin.parse_config_files_and_bindings(config_files, [])
        
        # Extract relevant parameters
        config_dict = {
            'model': {
                'latent_size': gin.query_parameter('RAVE.latent_size'),
                # ... other params
            },
            'training': {
                'batch_size': gin.query_parameter('train.batch_size'),
                # ... other params
            }
        }
        return config_dict
    
    def to_json(self, config_dict: dict) -> str:
        """Convert to JSON for storage"""
        return json.dumps(config_dict, indent=2)
    
    def to_gin_args(self, config_dict: dict) -> List[str]:
        """Convert back to command-line args"""
        args = []
        for config_name in config_dict['configs']:
            args.extend(['--config', config_name])
        # ... other parameters
        return args
```

### 5. Real-time Log Monitoring

**Decision**: Use file watching for log monitoring

**Rationale**:

- **Real-time**: Updates as logs are written
- **Efficient**: Only processes new content
- **Reliable**: Handles log rotation

**Implementation**:

```python
# core/log_monitor.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt6.QtCore import QObject, pyqtSignal
import re

class LogMonitor(QObject, FileSystemEventHandler):
    new_line = pyqtSignal(str)
    metrics_update = pyqtSignal(dict)
    
    def __init__(self, log_file: Path):
        super().__init__()
        self.log_file = log_file
        self.file_pos = 0
        self.observer = Observer()
        
        # Metrics patterns
        self.metric_patterns = {
            'loss': re.compile(r'loss: ([\d.]+)'),
            'step': re.compile(r'step: (\d+)'),
            'lr': re.compile(r'lr: ([\d.e-]+)')
        }
    
    def start(self):
        self.observer.schedule(self, str(self.log_file.parent))
        self.observer.start()
    
    def on_modified(self, event):
        if Path(event.src_path) == self.log_file:
            self.read_new_lines()
    
    def read_new_lines(self):
        with open(self.log_file, 'r') as f:
            f.seek(self.file_pos)
            for line in f:
                self.new_line.emit(line.strip())
                metrics = self.parse_metrics(line)
                if metrics:
                    self.metrics_update.emit(metrics)
            self.file_pos = f.tell()
    
    def parse_metrics(self, line: str) -> dict:
        metrics = {}
        for name, pattern in self.metric_patterns.items():
            match = pattern.search(line)
            if match:
                metrics[name] = float(match.group(1))
        return metrics if metrics else None
```

### 6. Audio Handling

**Decision**: Use sounddevice + librosa for audio

**Rationale**:

- **sounddevice**: Cross-platform playback
- **librosa**: Audio analysis and visualization
- **numpy**: Fast array operations

**Implementation**:

```python
# ui/widgets/audio_player.py
import sounddevice as sd
import librosa
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

class AudioPlayer(QThread):
    position = pyqtSignal(float)
    finished = pyqtSignal()
    
    def __init__(self, audio_path: str):
        super().__init__()
        self.audio, self.sr = librosa.load(audio_path, sr=None, mono=False)
        self.playing = False
        self.position_sample = 0
    
    def run(self):
        self.playing = True
        sd.play(self.audio, self.sr)
        
        while self.playing and sd.get_stream().active:
            pos = self.position_sample / self.sr
            self.position.emit(pos)
            self.msleep(100)
        
        self.finished.emit()
    
    def stop(self):
        self.playing = False
        sd.stop()
```

### 7. Visualization

**Decision**: Use Matplotlib for plots (embedded in PyQt)

**Rationale**:

- **Integration**: Can embed in Qt widgets
- **Familiar**: Most users know matplotlib
- **Flexible**: Can create any plot type
- **Export**: Easy to save plots

**Implementation**:

```python
# ui/widgets/metrics_plot.py
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget, QVBoxLayout

class MetricsPlot(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasQTAgg(self.figure)
        
        # Setup layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Create axes
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Step')
        self.ax.set_ylabel('Loss')
        
        # Data storage
        self.steps = []
        self.losses = []
    
    def add_point(self, step: int, loss: float):
        self.steps.append(step)
        self.losses.append(loss)
        self.update_plot()
    
    def update_plot(self):
        self.ax.clear()
        self.ax.plot(self.steps, self.losses)
        self.ax.set_xlabel('Step')
        self.ax.set_ylabel('Loss')
        self.canvas.draw()
```

---

## Design Patterns

### 1. Singleton for App State

```python
# core/app_state.py
class AppState:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init()
        return cls._instance
    
    def init(self):
        self.current_project = None
        self.db = Database()
        self.config_manager = ConfigManager()
```

### 2. Observer Pattern via Signals

```python
# core/signals.py
from PyQt6.QtCore import QObject, pyqtSignal

class GlobalSignals(QObject):
    # Project events
    project_changed = pyqtSignal(int)  # project_id
    
    # Dataset events
    dataset_created = pyqtSignal(int)  # dataset_id
    dataset_deleted = pyqtSignal(int)
    
    # Training events
    training_started = pyqtSignal(int)  # experiment_id
    training_progress = pyqtSignal(int, int, dict)  # experiment_id, step, metrics
    training_completed = pyqtSignal(int)
    training_failed = pyqtSignal(int, str)  # experiment_id, error
    
    # Model events
    model_saved = pyqtSignal(int)  # model_id
    model_exported = pyqtSignal(int)  # export_id

# Global instance
signals = GlobalSignals()
```

### 3. Factory Pattern for Widgets

```python
# ui/widget_factory.py
class WidgetFactory:
    @staticmethod
    def create_dataset_card(dataset_info: dict) -> QWidget:
        card = QWidget()
        # ... create widget
        return card
    
    @staticmethod
    def create_experiment_row(experiment_info: dict) -> QWidget:
        row = QWidget()
        # ... create widget
        return row
```

---

## Error Handling Strategy

### 1. User-Facing Errors

```python
# core/errors.py
from PyQt6.QtWidgets import QMessageBox

class ErrorHandler:
    @staticmethod
    def show_error(parent, title: str, message: str, details: str = None):
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        if details:
            msg.setDetailedText(details)
        msg.exec()
    
    @staticmethod
    def show_warning(parent, title: str, message: str):
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
    
    @staticmethod
    def confirm(parent, title: str, message: str) -> bool:
        reply = QMessageBox.question(
            parent, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
```

### 2. Logging

```python
# core/logger.py
import logging
from pathlib import Path

def setup_logging(log_dir: Path):
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "rave_gui.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )
    
    return logging.getLogger("rave_gui")
```

---

## Performance Considerations

### 1. Lazy Loading

**Large Lists**: Load data on-demand

```python
class DatasetListModel(QAbstractTableModel):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.cache = {}
        self.total_rows = db.count_datasets()
    
    def data(self, index, role):
        if not index.isValid():
            return None
        
        row = index.row()
        if row not in self.cache:
            # Fetch from database only when needed
            self.cache[row] = self.db.get_dataset(row)
        
        dataset = self.cache[row]
        # ... return data
```

### 2. Background Processing

**Heavy Operations**: Always use threads

```python
# Example: Dataset statistics calculation
class StatsCalculator(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    
    def run(self):
        stats = {}
        # Calculate statistics in background
        # ...
        self.finished.emit(stats)
```

### 3. Caching

**Frequently Accessed Data**: Cache in memory

```python
class CacheManager:
    def __init__(self):
        self.cache = {}
        self.max_size = 100
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple LRU)
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
```

---

## Testing Strategy

### 1. Unit Tests

```python
# tests/test_backend/test_dataset.py
import pytest
from rave_gui.backend.dataset import DatasetManager

def test_create_dataset():
    dm = DatasetManager()
    config = {
        'name': 'test',
        'input_path': '/audio',
        'output_path': '/output'
    }
    result = dm.validate_config(config)
    assert result.is_valid
```

### 2. Integration Tests with pytest-qt

```python
# tests/test_ui/test_dataset_wizard.py
import pytest

def test_dataset_wizard(qtbot):
    from rave_gui.ui.dialogs.new_dataset import NewDatasetWizard
    
    wizard = NewDatasetWizard()
    qtbot.addWidget(wizard)
    
    # Navigate through wizard
    wizard.next()
    assert wizard.currentId() == 1
```

### 3. End-to-End Tests

```python
# tests/test_integration/test_workflow.py
def test_full_workflow(qtbot, tmp_path):
    # Test complete workflow
    # 1. Create project
    # 2. Create dataset
    # 3. Start training
    # 4. Monitor progress
    # 5. Export model
    pass
```

---

## Security Considerations

### 1. Path Validation

```python
def validate_path(path: str) -> bool:
    """Ensure path is safe"""
    p = Path(path).resolve()
    # Check for path traversal
    return p.is_relative_to(Path.home())
```

### 2. Subprocess Safety

```python
# Always validate inputs before subprocess
def safe_command(cmd: List[str]) -> List[str]:
    """Validate command arguments"""
    allowed_commands = ['rave']
    if cmd[0] not in allowed_commands:
        raise ValueError(f"Command not allowed: {cmd[0]}")
    return cmd
```

---

## Deployment

### 1. PyInstaller for Executables

```python
# build.spec
a = Analysis(
    ['rave_gui/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('rave_gui/resources', 'resources'),
    ],
    hiddenimports=['rave', 'pytorch_lightning'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
```

### 2. Installation Script

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name='rave-gui',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'PyQt6>=6.4.0',
        'acids-rave>=2.0.0',
        'matplotlib>=3.5.0',
        'librosa>=0.9.0',
        'sounddevice>=0.4.0',
        'watchdog>=2.1.0',
    ],
    entry_points={
        'console_scripts': [
            'rave-gui=rave_gui.app:main',
        ],
    },
)
```

---

## Conclusion

This architecture provides:

- ✅ **Separation of Concerns**: UI, logic, data are separate
- ✅ **Testability**: Each layer can be tested independently
- ✅ **Maintainability**: Clear structure, easy to navigate
- ✅ **Extensibility**: Easy to add new features
- ✅ **Performance**: Non-blocking, efficient
- ✅ **Reliability**: Proper error handling, logging

The key to success is **starting simple** and **iterating**. Build the MVP first, get feedback, then enhance.
