# Epic #3 - Training Management System Implementation

## Overview

This implementation provides a complete training management system for the RAVE GUI, following the MVC architecture pattern with strict separation between backend logic (pure Python) and UI (PyQt6).

## Components Implemented

### 1. TrainingManager Backend (`rave_gui/backend/training.py`)

**Pure Python class - NO Qt dependencies**

**Key Features:**
- Creates and manages training experiment records in SQLite database
- Tracks experiment status (running, completed, failed, stopped)
- Stores training metrics as JSON in database
- Manages active training processes
- Provides CRUD operations for experiments

**Main Methods:**
- `start_training(config)` - Creates experiment record and returns experiment ID
- `get_experiment(experiment_id)` - Retrieves experiment with parsed JSON fields
- `list_experiments(project_id)` - Lists all experiments, optionally filtered
- `update_experiment_status(experiment_id, status)` - Updates experiment status
- `update_training_metrics(experiment_id, metrics)` - Stores metrics as JSON
- `stop_training(experiment_id)` - Stops running training process
- `register_process(experiment_id, process)` - Tracks active training threads

**Database Schema Used:**
```sql
CREATE TABLE experiments (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    name TEXT NOT NULL,
    dataset_id INTEGER,
    config TEXT,  -- JSON
    status TEXT DEFAULT 'running',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metrics TEXT,  -- JSON
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
)
```

### 2. TrainingProcess Thread (`rave_gui/backend/training.py`)

**Extends ProcessThread from core.process**

**Key Features:**
- Runs RAVE training CLI command in background thread
- Parses metrics from training logs in real-time
- Emits Qt signals for UI updates (but backend itself has no UI logic)
- Calculates training progress based on steps

**Signals Emitted:**
- `metrics_update(dict)` - Parsed metrics from logs
- `step_update(int, int)` - Current step and total steps
- Plus inherited: `output(str)`, `progress(int, str)`, `finished(bool, str)`

**Metrics Parsing:**
Uses regex patterns to extract:
- `loss` - Training loss
- `val_loss` - Validation loss  
- `step` - Current training step
- `epoch` - Current epoch
- `lr` - Learning rate

Patterns are case-insensitive and handle scientific notation (e.g., `1e-4`).

### 3. MetricsPlot Widget (`rave_gui/ui/widgets/metrics_plot.py`)

**PyQt6 widget with matplotlib integration**

**Key Features:**
- Embeds matplotlib plots in Qt widget using `FigureCanvasQTAgg`
- Two subplots: Training Loss and Learning Rate
- Plots both training loss and validation loss
- Learning rate uses logarithmic scale
- Includes matplotlib navigation toolbar
- Real-time updates as metrics arrive

**Main Methods:**
- `update_metrics(metrics)` - Adds new metrics and redraws plots
- `clear()` - Clears all history and plots

**Metrics Tracked:**
- Training loss (blue line)
- Validation loss (orange dashed line)
- Learning rate (green line, log scale)

### 4. NewTrainingWizard Dialog (`rave_gui/ui/dialogs/new_training.py`)

**Multi-page QWizard for training configuration**

**Pages:**

1. **DatasetSelectionPage**
   - Lists available datasets from database
   - Shows dataset info (samples, channels, sample rate)
   - Required field validation

2. **ConfigSelectionPage**
   - Base config dropdown (v1, v2, v3, discrete)
   - Multi-select modifiers (causal, snake, noise)
   - Returns config overrides list

3. **TrainingParametersPage**
   - Run name (required)
   - Max steps (default: 500,000)
   - Batch size (default: 8)
   - Learning rate (default: 1e-4)

4. **ConfirmationPage**
   - Summary of all selections
   - Review before starting

**Returns:**
Complete configuration dictionary with all parameters needed to start training.

### 5. TrainingPage UI (`rave_gui/ui/pages/training.py`)

**Main training interface**

**Layout:**
- **Left Panel:** Experiments table (30% width)
  - Columns: Name, Status, Started, Steps, Actions
  - Shows all experiments with stop buttons for running ones
  - Selectable rows to view details

- **Right Panel:** Details and monitoring (70% width)
  - Training information group (status, progress bar)
  - MetricsPlot for real-time visualization
  - Log viewer (read-only text area)

**Key Features:**
- "New Training" button opens wizard
- Real-time metrics updates for selected experiment
- Auto-scrolling log viewer
- Progress bar shows percentage based on current step
- Stop button for running experiments
- Experiment list auto-refreshes on status changes

**Signal Handling:**
- Connects to global `AppSignals` singleton
- Listens for training events (started, progress, completed, stopped)
- Updates UI in response to training process events

## Architecture

### 3-Layer MVC Pattern

```
┌─────────────────────────────────────────┐
│  UI Layer (PyQt6)                       │
│  - TrainingPage                         │
│  - NewTrainingWizard                    │
│  - MetricsPlot                          │
└────────────┬────────────────────────────┘
             │ Qt Signals
┌────────────▼────────────────────────────┐
│  Backend Layer (Pure Python)            │
│  - TrainingManager                      │
│  - TrainingProcess (extends QThread)    │
└────────────┬────────────────────────────┘
             │ Function Calls
┌────────────▼────────────────────────────┐
│  Data Layer                             │
│  - Database (SQLite)                    │
│  - RAVE CLI (subprocess)                │
│  - ProcessThread (subprocess wrapper)   │
└─────────────────────────────────────────┘
```

**Key Principles:**
- Backend has NO direct UI code or PyQt imports beyond signals
- Backend returns data, raises exceptions
- UI emits signals, displays data
- Clear separation enables testing and reusability

## Integration

### MainWindow Integration

The `TrainingPage` is initialized in `main_window.py`:

```python
self.pages.addWidget(TrainingPage(self.db))
```

Database connection is passed to enable backend operations.

### Signal Flow

1. User clicks "New Training" → Opens wizard
2. Wizard completion → Creates experiment in database
3. TrainingProcess started → Runs RAVE CLI in background
4. Training logs parsed → Metrics extracted
5. Metrics signals → Update database and UI
6. Training completes → Status updated, process unregistered

## Testing

### Backend Tests (`tests/test_backend/`)

**test_training_manager.py:**
- CRUD operations for experiments
- Status updates
- Metrics storage and retrieval
- Process registration
- Stop training functionality

**test_training_process.py:**
- Metrics parsing from various log formats
- Step extraction and progress calculation
- Case-insensitive parsing
- Scientific notation handling
- Multiple metric formats

### UI Tests (`tests/test_ui/`)

**test_training_page.py:**
- Page initialization
- Widget structure
- Experiments table
- Metrics display
- Signal handling
- User interactions

## Usage

### Starting a New Training Run

1. Click "New Training" button
2. Select dataset from list
3. Choose RAVE config (v2 recommended)
4. Optionally add modifiers
5. Set training parameters:
   - Name your run
   - Set max steps (default: 500k)
   - Configure batch size, learning rate
6. Review configuration
7. Click "Finish" to start training

### Monitoring Training

- Select experiment from table to view details
- Real-time metrics plot updates automatically
- Progress bar shows completion percentage
- Log viewer displays training output
- Click "Stop" to cancel running training

### Viewing Past Experiments

- All experiments listed in table
- Status shows: running, completed, failed, stopped
- Click to view final metrics and configuration
- Metrics plot shows training history

## File Changes

### New/Modified Files:
- `rave_gui/backend/training.py` - Complete rewrite with TrainingManager and TrainingProcess
- `rave_gui/ui/pages/training.py` - Complete implementation of training page
- `rave_gui/ui/widgets/metrics_plot.py` - Complete matplotlib integration
- `rave_gui/ui/dialogs/new_training.py` - Complete 4-page wizard
- `rave_gui/main_window.py` - Updated to pass db connection to TrainingPage

### New Test Files:
- `tests/test_backend/test_training_manager.py`
- `tests/test_backend/test_training_process.py`
- `tests/test_ui/test_training_page.py`

## Dependencies

### Required (already in requirements.txt):
- PyQt6 - UI framework
- matplotlib - Plotting
- sqlite3 - Database (Python stdlib)

### Used:
- `re` - Regex for log parsing
- `json` - Config/metrics serialization
- `datetime` - Timestamps
- `pathlib` - Path handling

## Future Enhancements

Possible additions for future work:

1. **TensorBoard Integration** (Epic 3.4)
   - Launch TensorBoard from GUI
   - Embedded viewer if feasible
   - Quick links to experiment logs

2. **Advanced Metrics** (Epic 3.3)
   - System resource monitoring (GPU, CPU, RAM)
   - Audio sample preview during training
   - Anomaly detection (NaN loss alerts)

3. **Training Queue** (Epic 3.2)
   - Schedule multiple runs
   - Queue management
   - Priority ordering

4. **Experiment Comparison** (Epic 3.5)
   - Side-by-side metrics
   - Parameter diff viewer
   - Performance benchmarking

5. **Checkpoint Management**
   - Resume from checkpoint
   - Checkpoint browser
   - Best checkpoint selection

## Notes

- All training runs are automatically tracked in database
- Metrics are stored as JSON for flexibility
- Training processes are killed on application close
- UI remains responsive during training (background threads)
- No temporary files created - all data in database
