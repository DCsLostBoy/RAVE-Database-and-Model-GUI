# RAVE GUI - Quick Setup Guide

## Prerequisites

Before setting up the RAVE GUI, ensure you have:

- **Python 3.9+** installed
- **Git** installed (for cloning the repository)
- **Windows PowerShell** (for running commands on Windows)

## Step-by-Step Setup

### 1. Clone the Repository

```powershell
git clone https://github.com/DCsLostBoy/RAVE-Database-and-Model-GUI.git
cd RAVE-Database-and-Model-GUI
```

### 2. Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Note: If you get an execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will install:
# - PyQt6 (GUI framework)
# - matplotlib (plotting)
# - sounddevice, soundfile, librosa (audio)
# - watchdog (file monitoring)
# - pytest, pytest-qt (testing)
# - black, flake8, mypy (development tools)
# - Plus all RAVE dependencies
```

### 4. Install the Package

```powershell
# Install in development mode
pip install -e .

# This creates the 'rave-gui' command
```

### 5. Verify Installation

```powershell
# Check that both commands are available
rave --help      # Original RAVE CLI
rave-gui --help  # New GUI application (will launch the GUI)
```

### 6. Run the Application

```powershell
# Method 1: Use the installed command
rave-gui

# Method 2: Run as Python module
python -m rave_gui.app
```

## Troubleshooting

### PyQt6 Import Errors

If you see errors like `Import "PyQt6.QtWidgets" could not be resolved`:

```powershell
# Ensure PyQt6 is installed
pip install PyQt6 PyQt6-WebEngine

# Verify installation
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

### Virtual Environment Not Activating

On Windows, you may need to adjust execution policy:

```powershell
# Check current policy
Get-ExecutionPolicy

# If it's "Restricted", change it:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
.\venv\Scripts\Activate.ps1
```

### Missing Dependencies

If individual dependencies fail to install:

```powershell
# Try installing them separately
pip install PyQt6
pip install matplotlib
pip install sounddevice soundfile librosa
pip install watchdog
pip install pytest pytest-qt
```

### RAVE CLI Not Found

If the `rave` command isn't found after installation:

```powershell
# Make sure you installed in development mode
pip install -e .

# Check if scripts directory is in PATH
python -c "import sys; print(sys.prefix)"

# The Scripts folder should contain rave.exe and rave-gui.exe
```

## Running Tests

```powershell
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/test_ui/
pytest tests/test_backend/

# Run with verbose output
pytest -v tests/

# Run with coverage report
pytest --cov=rave_gui tests/
```

## Development Workflow

### Code Formatting

```powershell
# Format code with black
black rave_gui/ tests/

# Check linting with flake8
flake8 rave_gui/ tests/

# Type checking with mypy
mypy rave_gui/
```

### Making Changes

1. Create a feature branch
2. Make your changes
3. Run tests: `pytest tests/`
4. Format code: `black rave_gui/ tests/`
5. Check linting: `flake8 rave_gui/ tests/`
6. Commit and push

## Next Steps

Once the application is running:

1. **Explore the interface** - Navigate through Dashboard, Datasets, Training, Models, and Export pages
2. **Create a dataset** - Use the Dataset wizard to preprocess audio files
3. **Configure training** - Set up a training run with your dataset
4. **Monitor progress** - Watch training metrics in real-time
5. **Export models** - Export trained models to TorchScript or ONNX

## Getting Help

- **Documentation**: See `docs/` folder for detailed guides
- **Issues**: Report bugs on [GitHub Issues](https://github.com/DCsLostBoy/RAVE-Database-and-Model-GUI/issues)
- **Implementation Guide**: See `docs/IMPLEMENTATION_ROADMAP.md`
- **Architecture**: See `docs/TECHNICAL_DECISIONS.md`

## Current Development Status

**Phase 1 - Foundation (Weeks 1-4)**

- ✅ Project structure created
- ✅ Core architecture implemented
- ✅ UI framework established
- 🔄 Feature implementation in progress

See `docs/IMPLEMENTATION_ROADMAP.md` for detailed weekly tasks and `docs/PROJECT_PLAN.md` for complete feature specifications.
