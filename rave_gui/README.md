# RAVE GUI - Graphical User Interface for RAVE

A PyQt6-based graphical interface for the RAVE (Realtime Audio Variatione autoEncoder) framework, making audio model training and management accessible through an intuitive desktop application.

## Features

- **Dataset Management**: Create and preprocess audio datasets with an easy-to-use wizard
- **Training Configuration**: Configure and launch model training with visual parameter editors
- **Real-time Monitoring**: Track training progress with live metrics and log viewing
- **Model Library**: Browse, test, and compare trained models
- **Export Tools**: Export models to TorchScript and ONNX formats
- **Project Organization**: Manage multiple projects with integrated database

## Installation

### Prerequisites

- Python 3.9 or higher
- PyQt6
- RAVE CLI (`acids-rave`)

### Install from Source

```powershell
# Clone the repository
git clone https://github.com/DCsLostBoy/RAVE-Database-and-Model-GUI.git
cd RAVE-Database-and-Model-GUI

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Quick Start

### Running the Application

```powershell
# If installed with pip install -e .
rave-gui

# Or run directly
python -m rave_gui.app
```

### Creating Your First Dataset

1. Click **Datasets** in the sidebar
2. Click **New Dataset**
3. Follow the wizard:
   - Select audio files/folder
   - Configure parameters (sample rate, channels)
   - Start preprocessing
4. Monitor progress in real-time

### Training a Model

1. Navigate to **Training** page
2. Click **New Training**
3. Select:
   - Dataset
   - Model configuration (v2, v3, etc.)
   - Training parameters
4. Launch and monitor training

## Project Structure

```
rave-gui/
├── rave_gui/              # Main application package
│   ├── app.py            # Application entry point
│   ├── main_window.py    # Main window controller
│   ├── ui/               # UI components (pages, widgets, dialogs)
│   ├── backend/          # Business logic (dataset, training, model, export)
│   ├── core/             # Core utilities (database, process, config, signals)
│   └── resources/        # Static resources (themes, icons)
├── tests/                # Test suite
├── docs/                 # Documentation
└── requirements.txt      # Dependencies
```

## Development

### Setting Up Development Environment

```powershell
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Running Tests

```powershell
# Run all tests
pytest tests/

# Run UI tests only
pytest tests/test_ui/

# Run backend tests only
pytest tests/test_backend/

# Run with coverage
pytest --cov=rave_gui tests/
```

### Code Style

This project follows PEP 8 style guidelines:

```powershell
# Format code with black
black rave_gui/ tests/

# Lint with flake8
flake8 rave_gui/ tests/

# Type check with mypy
mypy rave_gui/
```

## Architecture

The RAVE GUI follows a 3-layer MVC architecture:

- **UI Layer**: PyQt6 widgets and pages (no business logic)
- **Backend Layer**: Pure Python business logic (no Qt imports)
- **Core Layer**: Utilities for database, subprocess, config, and signals

### Key Patterns

- **Signals**: Qt signals for cross-component communication (`core/signals.py`)
- **Threading**: QThread for non-blocking subprocess operations
- **Database**: SQLite for persistent storage of projects, datasets, experiments
- **Process Management**: Subprocess wrappers for RAVE CLI commands

## Documentation

- [User Guide](docs/user_guide.md) - Complete usage documentation
- [Implementation Roadmap](docs/IMPLEMENTATION_ROADMAP.md) - Development guide
- [Project Plan](docs/PROJECT_PLAN.md) - Feature specifications
- [Technical Decisions](docs/TECHNICAL_DECISIONS.md) - Architecture and patterns

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original RAVE implementation by Antoine Caillon (IRCAM)
- Built with PyQt6
- Icons from [Material Icons](https://material.io/icons/) / [Feather Icons](https://feathericons.com/)

## Support

- Issues: [GitHub Issues](https://github.com/DCsLostBoy/RAVE-Database-and-Model-GUI/issues)
- Documentation: [docs/](docs/)

## Roadmap

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) for planned features and milestones.

### Current Status: Phase 1 - Foundation

- ✅ Project structure established
- 🔄 Core UI components (in progress)
- ⏳ Dataset preprocessing
- ⏳ Training management
- ⏳ Model library
- ⏳ Export tools
