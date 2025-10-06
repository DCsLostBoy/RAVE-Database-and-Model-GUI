# RAVE GUI - AI Coding Instructions

## Quick Start for AI Agents

**Before implementing ANY feature:**
1. **Read the task** in `docs/PROJECT_PLAN.md` (Epic → Feature → Task number) - This is your source of truth for what to build
2. **Check architecture** in `docs/TECHNICAL_DECISIONS.md` - Database schema, design patterns, and architectural decisions
3. **Review sprint plan** in `docs/PRIORITIZED_BACKLOG.md` - Dependencies, effort estimates, and priorities
4. **Find code examples** in `docs/IMPLEMENTATION_ROADMAP.md` - Week-by-week implementation guide with patterns
5. **Follow 3-layer architecture strictly**: Backend (Pure Python, no Qt) → Signals → UI (PyQt6)

**Key Principle:** Backend = Pure Python (no Qt imports), UI = PyQt6 (emits signals), Signals = Cross-layer communication

## Project Overview

RAVE GUI wraps the RAVE CLI (`acids-rave`) via subprocesses for dataset preprocessing, model training, and export.

**Current Phase:** Phase 1 - Foundation (Weeks 1-4)  
**Documentation Hub:** `docs/PROJECT_PLANNING_README.md` - Start here for complete overview of all planning docs

## Architecture

**3-Layer MVC Structure:** UI (PyQt6) → Signals → Backend (Pure Python, no Qt) → Data Layer  
**Full diagram:** `docs/TECHNICAL_DECISIONS.md` → "Architecture Pattern"

**CRITICAL RULE:** Backend classes (`backend/`) NEVER import PyQt6. Return data, raise exceptions. UI emits signals.

**Key patterns:** `docs/TECHNICAL_DECISIONS.md` has full implementations for CLI subprocess, SQLite, log monitoring, audio, visualization

## Critical Patterns

**All patterns with full code:** `docs/TECHNICAL_DECISIONS.md` and `docs/IMPLEMENTATION_ROADMAP.md`

1. **Subprocess Pattern:** Use QThread for all RAVE CLI operations (train, preprocess, export)
2. **Database:** SQLite with tables: projects, datasets, experiments, models, exports. Store configs as JSON.
3. **Signals:** Use `core/signals.py` AppSignals singleton for all cross-component events
4. **Navigation:** QStackedWidget in MainWindow switches between 5 pages (dashboard, datasets, training, models, export)

## Development Workflows

### Running the Application

```powershell
python -m rave_gui.app
```

Or after `pip install -e .`:

```powershell
rave
```

### Testing

```powershell
pytest tests/           # All tests
pytest tests/test_ui/   # UI unit tests only
pytest tests/test_backend/  # Backend unit tests
pytest -k "test_training"   # Specific test pattern
```

Uses `pytest-qt` for PyQt6 testing (`qtbot` fixture).

### Code Style

- **Formatter:** `black` (PEP 8 compliant, already in requirements.txt)
- **Linter:** `flake8`
- **Type Hints:** `mypy` configured - add hints to new functions

Run before committing:

```powershell
black rave_gui/ tests/
flake8 rave_gui/ tests/
mypy rave_gui/
```

## Project-Specific Conventions

### File Organization

- **One class per file** in `backend/` and `ui/pages/`
- **Reusable components** go in `ui/widgets/`
- **Dialogs** (wizards, settings) in `ui/dialogs/`
- **Shared utilities** in `core/`

### Import Style

```python
# Standard library
import sys
from pathlib import Path

# Third-party
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, QThread

# Local application
from rave_gui.core.signals import AppSignals
from rave_gui.backend.training import TrainingManager
```

### Widget Initialization Pattern

```python
class CustomWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Widget Name")
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        # Layout and widget setup
        pass
    
    def connect_signals(self):
        # Signal/slot connections
        pass
```

### Key Patterns

**Wizards:** Multi-page QWizard with `validatePage()` → See `docs/IMPLEMENTATION_ROADMAP.md` Week 3  
**Gin Configs:** Scan RAVE `.gin` files, compose (base + modifiers), store as JSON → See `docs/TECHNICAL_DECISIONS.md`  
**CLI:** Multiple `--config` flags for composition: `rave train --config v2 --config causal --db_path /dataset`

## RAVE CLI Commands

**Preprocess:** `rave preprocess --input_path /audio --output_path /dataset --num_signal 65536 --channels 1 --sr 44100`  
**Train:** `rave train --config v2 --db_path /dataset --name model --override PHASE.max_steps=500000`  
**Export:** `rave export --run /path/to/run --streaming --format torchscript`

**Full examples:** `docs/IMPLEMENTATION_ROADMAP.md` and `docs/TECHNICAL_DECISIONS.md`

## Key Dependencies

- **PyQt6** - UI framework (not PyQt5 - API differences exist)
- **acids-rave** - The wrapped RAVE CLI tool
- **matplotlib** - Metrics visualization (embed with `FigureCanvasQTAgg`)
- **librosa** - Audio loading and analysis
- **sounddevice** - Cross-platform audio playback
- **soundfile** - Audio file I/O
- **watchdog** - File system monitoring for logs/datasets
- **lmdb** - Dataset format used by RAVE (read-only access for inspection)

## Common Pitfalls

1. **UI Freezing:** Use QThread for all subprocess operations (never block main thread)
2. **Backend Qt Imports:** Backend returns data, UI emits signals (no PyQt6 in `backend/`)
3. **Log Monitoring:** Use `watchdog.Observer` for real-time file watching
4. **Resource Paths:** Use `pathlib.Path` relative to package root
5. **Process Cleanup:** Terminate subprocesses in `closeEvent()`, close DB connection

**Full code examples:** `docs/TECHNICAL_DECISIONS.md` → "Key Architectural Decisions"

## Documentation Map

**Start here:** `docs/PROJECT_PLANNING_README.md` - Overview of all planning docs

- `docs/PROJECT_PLAN.md` - All 8 Epics with task breakdowns and acceptance criteria
- `docs/IMPLEMENTATION_ROADMAP.md` - Week-by-week implementation guide with complete code examples
- `docs/PRIORITIZED_BACKLOG.md` - Sprint planning with dependencies and effort estimates
- `docs/TECHNICAL_DECISIONS.md` - Architecture, patterns, and full code implementations
- `docs/GITHUB_ISSUES.md` - Ready-to-use issue templates

## Current State & Next Steps

**Status:** Foundation phase (Weeks 1-4). Structure established, pages/managers need implementation.

**Development Order:**
1. Read task in `docs/PROJECT_PLAN.md` → 2. Check dependencies in `docs/PRIORITIZED_BACKLOG.md` → 3. Find pattern in `docs/IMPLEMENTATION_ROADMAP.md` → 4. Implement backend (no Qt) → 5. Implement UI (emits signals) → 6. Add tests

**File locations:** `docs/PROJECT_PLAN.md` has complete task-to-file mapping for all Epics
