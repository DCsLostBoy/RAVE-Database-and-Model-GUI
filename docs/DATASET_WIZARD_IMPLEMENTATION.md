# Dataset Creation Wizard Implementation

## Overview

This document describes the implementation of the Dataset Creation Wizard for the RAVE GUI, which provides a user-friendly interface for creating preprocessed audio datasets for RAVE training.

## Architecture

The wizard follows PyQt6's `QWizard` pattern with four main pages:

1. **IntroPage**: Introduction and overview
2. **InputFilesPage**: Audio file selection with preview
3. **ParametersPage**: Dataset parameter configuration
4. **PreprocessingPage**: Progress monitoring

## Features Implemented

### 1. Audio File Browser (InputFilesPage)

#### File Selection Methods
- **Browse Folders**: Recursively scans directories for audio files
- **Add Files**: Direct file selection via file dialog
- **Drag and Drop**: Drop folders or files directly into the wizard
- **Clear All**: Remove all selected files

#### Supported Audio Formats
- WAV (.wav)
- MP3 (.mp3)
- FLAC (.flac)
- OGG (.ogg)
- AIFF (.aif, .aiff)
- OPUS (.opus)
- AAC (.aac)

#### Features
- Duplicate file detection (files are added only once)
- File count display
- Full path tooltips on hover
- Audio preview integration

### 2. Audio Player Widget

The `AudioPlayer` widget provides real-time audio preview with:

#### Playback Features
- **Play/Stop**: Toggle audio playback
- **Seek Control**: Slider for position navigation
- **Time Display**: Current position and total duration
- **Waveform Visualization**: Real-time waveform display

#### Technical Details
- Uses `soundfile` for audio loading
- Uses `sounddevice` for cross-platform playback
- Supports mono and stereo audio
- Automatic waveform downsampling for performance
- Position tracking with QTimer (50ms updates)

#### Signals
- `playback_started`: Emitted when playback begins
- `playback_stopped`: Emitted when playback stops

### 3. Parameter Configuration (ParametersPage)

#### Required Fields
- **Dataset Name**: Validated for alphanumeric characters, hyphens, and underscores
- **Output Path**: Directory where preprocessed dataset will be saved

#### Optional Parameters
- **Sample Rate**: 8000-192000 Hz (default: 44100)
- **Channels**: 1-8 channels (default: 1 for mono)
- **Signal Length**: 1024-1048576 samples (default: 65536)
- **Lazy Loading**: On-demand audio loading vs. preprocessing
- **Dynamic Database**: Allow database to grow dynamically

#### Validation
- Real-time name validation with error messages
- Directory existence checks
- Option to create non-existent directories
- `isComplete()` prevents navigation with invalid data
- `validatePage()` performs final validation before proceeding

### 4. Preprocessing Progress (PreprocessingPage)

#### UI Components
- **Status Label**: Current processing state
- **Progress Bar**: Visual progress indicator (0-100%)
- **File Counter**: "Files processed: X / Y"
- **Log Viewer**: Real-time processing logs
- **Control Buttons**: Start/Cancel processing

#### Features
- `initializePage()` loads wizard data when page is shown
- Progress updates via `update_progress(percent, current, total)`
- Log messages via `log_append(message)`
- Processing state tracking prevents premature completion
- Placeholder for backend integration (currently simulates progress)

## API Reference

### NewDatasetWizard

```python
class NewDatasetWizard(QWizard):
    """Main wizard class."""
    
    # Signals
    preprocessing_started = pyqtSignal(dict)  # Emits config dict
    
    # Methods
    def get_audio_files(self) -> list[str]:
        """Get list of selected audio file paths."""
        
    def get_dataset_config(self) -> dict:
        """Get dataset configuration dictionary."""
```

**Configuration Dictionary Keys:**
- `name`: Dataset name (str)
- `output_path`: Output directory path (str)
- `sample_rate`: Audio sample rate in Hz (int)
- `channels`: Number of audio channels (int)
- `signal_length`: Length of each sample in samples (int)
- `lazy`: Use lazy loading (bool)
- `dyndb`: Allow dynamic database growth (bool)

### AudioPlayer

```python
class AudioPlayer(QWidget):
    """Audio player widget."""
    
    # Signals
    playback_started = pyqtSignal()
    playback_stopped = pyqtSignal()
    
    # Methods
    def load_audio(self, file_path: str) -> bool:
        """Load an audio file. Returns True on success."""
        
    def toggle_playback(self):
        """Toggle between play and stop."""
        
    def start_playback(self):
        """Start audio playback."""
        
    def stop_playback(self):
        """Stop audio playback."""
```

## Usage Example

```python
from PyQt6.QtWidgets import QApplication
from rave_gui.ui.dialogs.new_dataset import NewDatasetWizard

app = QApplication([])

wizard = NewDatasetWizard()

# Connect to preprocessing signal (optional)
def on_start_preprocessing(config):
    print(f"Starting preprocessing with config: {config}")
    
wizard.preprocessing_started.connect(on_start_preprocessing)

# Show wizard
result = wizard.exec()

if result == QWizard.DialogCode.Accepted:
    audio_files = wizard.get_audio_files()
    config = wizard.get_dataset_config()
    
    print(f"Selected {len(audio_files)} files")
    print(f"Config: {config}")
else:
    print("Wizard cancelled")
```

## Testing

### Unit Tests

Located in `tests/test_ui/`:
- `test_new_dataset_wizard.py`: Tests for wizard pages
- `test_audio_player.py`: Tests for audio player widget

Run tests:
```bash
pytest tests/test_ui/test_new_dataset_wizard.py -v
pytest tests/test_ui/test_audio_player.py -v
```

### Manual Testing

Run the manual test script:
```bash
python tests/manual_test_wizard.py
```

This opens a simple window with a button to launch the wizard for interactive testing.

## Integration with Backend

The wizard is designed to integrate with a backend preprocessing manager:

```python
# Example backend integration (not yet implemented)
from rave_gui.backend.dataset import DatasetPreprocessor

wizard = NewDatasetWizard()

if wizard.exec() == QWizard.DialogCode.Accepted:
    config = wizard.get_dataset_config()
    files = wizard.get_audio_files()
    
    # Create preprocessor
    preprocessor = DatasetPreprocessor()
    
    # Connect signals for progress updates
    preprocessor.progress.connect(
        wizard.process_page.update_progress
    )
    preprocessor.log_message.connect(
        wizard.process_page.log_append
    )
    
    # Start preprocessing
    preprocessor.preprocess(
        input_files=files,
        output_path=config['output_path'],
        sample_rate=config['sample_rate'],
        channels=config['channels'],
        signal_length=config['signal_length'],
        lazy=config['lazy'],
        dyndb=config['dyndb']
    )
```

## Future Enhancements

1. **Backend Integration**: Connect to actual RAVE preprocessing subprocess
2. **Resume Support**: Save wizard state for resuming interrupted work
3. **Batch Processing**: Queue multiple datasets for sequential processing
4. **Advanced Audio Info**: Display detailed metadata (bitrate, codec, etc.)
5. **Spectogram View**: Add spectogram visualization option
6. **Preset Configs**: Save/load parameter presets
7. **Validation Rules**: Additional dataset name validation against existing datasets
8. **Progress Persistence**: Save progress logs to file

## Dependencies

- **PyQt6**: UI framework
- **soundfile**: Audio file I/O
- **sounddevice**: Audio playback
- **numpy**: Numerical operations for waveform processing

All dependencies are listed in `requirements.txt`.

## Code Style

The implementation follows the project's coding standards:
- PEP 8 compliance via `black` formatter
- Type hints for public methods
- Comprehensive docstrings
- Signal/slot pattern for event handling
- Separation of UI and business logic

## Accessibility

- Keyboard navigation supported throughout wizard
- Tab order properly configured
- Tooltips on all complex controls
- Clear error messages with guidance
- Progress feedback for long operations
