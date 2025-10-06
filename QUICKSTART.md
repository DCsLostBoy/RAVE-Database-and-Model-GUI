# RAVE GUI - Quick Start Guide

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
# Install GUI dependencies (minimal for testing Epic #1)
pip install PyQt6 pytest pytest-qt

# Or install all dependencies (for full RAVE functionality)
pip install -r requirements.txt
```

## Running the Application

### Launch the GUI

```bash
python -m rave_gui.app
```

On first launch:
1. Project selector dialog appears
2. Click "New Project..." to create your first project
3. Enter a project name and select a directory
4. Click "OK" to start using RAVE GUI

### Verify Epic #1 (Backend Only)

Test all Epic #1 functionality without GUI:

```bash
python verify_epic1.py
```

Expected output:
```
============================================================
Epic #1 - Core GUI Infrastructure Verification
============================================================

✅ All core modules import successfully
✅ SettingsManager tests passed
✅ ConfigManager tests passed
✅ Database and ProjectManager tests passed
✅ AppSignals verified
✅ Theme files exist

============================================================
✅ All Epic #1 acceptance criteria verified!
============================================================
```

### Run Tests

```bash
# Run all tests
pytest tests/

# Run backend tests only
pytest tests/test_backend/

# Run with verbose output
pytest tests/ -v
```

## Quick Feature Tour

### 1. Project Management

**Create a Project:**
- Menu: `File > New Project...` (Ctrl+N)
- Enter project name and path
- Project is created and becomes active

**Switch Projects:**
- Menu: `File > Switch Project...` (Ctrl+O)
- Select from list of projects
- Double-click or select and click "OK"

**Delete a Project:**
- Open project selector
- Select project to delete
- Click "Delete Project"
- Confirm deletion (files remain on disk)

### 2. Navigation

Click sidebar buttons to navigate:
- **Dashboard**: Project overview (coming in Epic #2)
- **Datasets**: Dataset management (coming in Epic #2)
- **Training**: Model training (coming in Epic #3)
- **Models**: Model library (coming in Epic #4)
- **Export**: Model export (coming in Epic #4)

### 3. Theme Switching

**Change Theme:**
- Menu: `Edit > Settings...` (Ctrl+,)
- Select "Dark" or "Light" theme
- Click "OK"
- Theme changes immediately

### 4. Settings

**Configure Defaults:**
- Menu: `Edit > Settings...`
- Set default paths for:
  - Datasets
  - Models
  - Exports
- Select theme
- Click "OK" to save

**Settings Location:**
- Windows: `%USERPROFILE%\.rave_gui\settings.json`
- macOS/Linux: `~/.rave_gui/settings.json`

**Database Location:**
- Windows: `%USERPROFILE%\.rave_gui\rave_gui.db`
- macOS/Linux: `~/.rave_gui/rave_gui.db`

## Features in Epic #1

### ✅ Working Now

- [x] Application launches on Windows/Mac/Linux
- [x] Project creation with validation
- [x] Project switching and management
- [x] Last project loads automatically on startup
- [x] Window size/position persists across sessions
- [x] Theme switching (dark/light)
- [x] Settings persistence
- [x] Recent projects tracking
- [x] Navigation between pages
- [x] Status bar feedback
- [x] Menu bar with keyboard shortcuts
- [x] High-DPI display support

### 🚧 Coming in Future Epics

- [ ] Dataset preprocessing (Epic #2)
- [ ] Audio file management (Epic #2)
- [ ] Model training (Epic #3)
- [ ] Training monitoring (Epic #3)
- [ ] Model inspection (Epic #4)
- [ ] Model export (Epic #4)

## Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| New Project | Ctrl+N | Cmd+N |
| Switch Project | Ctrl+O | Cmd+O |
| Settings | Ctrl+, | Cmd+, |
| Quit | Ctrl+Q | Cmd+Q |

## Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt6'"

Install PyQt6:
```bash
pip install PyQt6
```

### Application won't start

1. Check Python version: `python --version` (need 3.8+)
2. Verify PyQt6 installation: `python -c "import PyQt6; print('OK')"`
3. Check for error messages in console

### Theme not loading

1. Verify theme files exist:
   - `rave_gui/resources/themes/dark.qss`
   - `rave_gui/resources/themes/light.qss`
2. Delete settings file to reset: `~/.rave_gui/settings.json`

### Database errors

1. Check database file: `~/.rave_gui/rave_gui.db`
2. Ensure directory is writable
3. Delete database to reset (will lose projects)

### Window doesn't restore size/position

1. Close application normally (not force quit)
2. Check settings file has `window_geometry` key
3. Delete `window_geometry` from settings to reset

## Testing

See `EPIC1_TESTING.md` for comprehensive testing procedures:
- Manual GUI testing
- Automated verification
- Platform-specific tests
- Performance checks

## Getting Help

1. **Documentation**:
   - `EPIC1_TESTING.md` - Testing guide
   - `EPIC1_FINAL_SUMMARY.md` - Implementation details
   - `docs/PROJECT_PLAN.md` - Full project plan

2. **Verification**:
   - Run `python verify_epic1.py` to check installation

3. **Issues**:
   - Check console output for errors
   - Verify all dependencies are installed
   - Test with fresh database (delete `~/.rave_gui/rave_gui.db`)

## What's Next?

**Epic #1 is complete!** The foundation is ready for:

- **Epic #2**: Dataset Management
  - Create and preprocess datasets
  - Audio file browser
  - Dataset statistics

- **Epic #3**: Training Management
  - Configure and start training
  - Real-time monitoring
  - Experiment tracking

- **Epic #4**: Model Management
  - Model library and inspection
  - Export to various formats
  - Model testing

## Development

To contribute or modify:

```bash
# Clone the repository
git clone https://github.com/DCsLostBoy/RAVE-Database-and-Model-GUI.git
cd RAVE-Database-and-Model-GUI

# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Format code
black rave_gui/ tests/

# Lint code
flake8 rave_gui/ tests/

# Type check
mypy rave_gui/
```

## Architecture

RAVE GUI uses a 3-layer MVC architecture:

```
┌─────────────────────────────────────┐
│   UI Layer (PyQt6)                  │
│   - main_window.py                  │
│   - dialogs/                        │
│   - pages/                          │
└──────────────┬──────────────────────┘
               │ Signals
┌──────────────▼──────────────────────┐
│   Signal Layer                      │
│   - core/signals.py (AppSignals)    │
└──────────────┬──────────────────────┘
               │ Method calls
┌──────────────▼──────────────────────┐
│   Backend Layer (Pure Python)       │
│   - backend/project.py              │
│   - core/config.py                  │
│   - core/database.py                │
│   - core/settings.py                │
└─────────────────────────────────────┘
```

**Key Principle**: Backend never imports PyQt6. All Qt dependencies are in UI layer only.

## License

See LICENSE file for details.

## Credits

- RAVE by Antoine Caillon (IRCAM)
- GUI by DCsLostBoy with GitHub Copilot
- Built with PyQt6

---

**Ready to build amazing audio models with RAVE!** 🎵🎹🎸
