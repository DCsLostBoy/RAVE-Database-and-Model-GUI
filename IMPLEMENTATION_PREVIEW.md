# Dataset Creation Wizard - Implementation Preview

## Overview

This document provides a visual guide to the newly implemented Dataset Creation Wizard for the RAVE GUI.

## Wizard Flow

The wizard consists of 4 pages that guide users through dataset creation:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. INTRODUCTION PAGE                                        │
│                                                             │
│  Create New Dataset                                         │
│  This wizard will help you preprocess audio files for      │
│  RAVE training.                                             │
│                                                             │
│  A dataset contains preprocessed audio samples ready       │
│  for training.                                              │
│                                                             │
│                                       [Cancel] [Next >]     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 2. SELECT AUDIO FILES PAGE                                  │
│                                                             │
│  Choose the audio files to include in your dataset.        │
│  You can drag and drop folders or use the browse button.   │
│                                                             │
│  [Browse Folders...] [Add Files...] [Clear All]            │
│                                                             │
│  Audio Files:                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • sample1.wav                                       │   │
│  │ • sample2.mp3                                       │   │
│  │ • sample3.flac                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│  3 files selected                                           │
│                                                             │
│  Preview:                                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ sample1.wav (44100 Hz, (132300, 2))                │   │
│  │ ╔═══════════════════════════════════════╗           │   │
│  │ ║      Waveform Visualization           ║           │   │
│  │ ║   ╱╲  ╱╲    ╱╲   ╱╲  ╱╲   ╱╲          ║           │   │
│  │ ║  ╱  ╲╱  ╲──╱  ╲─╱  ╲╱  ╲─╱  ╲         ║           │   │
│  │ ╚═══════════════════════════════════════╝           │   │
│  │ [▶ Play]  ━━━━━━━━━━━━━━━━━━━━  0:00 / 3:00        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                                  [< Back] [Cancel] [Next >] │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 3. DATASET PARAMETERS PAGE                                  │
│                                                             │
│  Configure preprocessing parameters for your dataset.       │
│                                                             │
│  Dataset Name: * ___________________________                │
│  [Error: Dataset name is required]                          │
│                                                             │
│  Output Path: ___________________________ [Browse...]       │
│                                                             │
│  Sample Rate (Hz):  [44100▼]                                │
│                                                             │
│  Channels:  [1▼]  (1=mono, 2=stereo)                        │
│                                                             │
│  Signal Length (samples):  [65536▼]                         │
│                                                             │
│  Options:                                                   │
│  ☐ Use lazy loading                                         │
│  ☑ Dynamic database growth                                  │
│                                                             │
│                                  [< Back] [Cancel] [Next >] │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 4. PREPROCESSING PAGE                                       │
│                                                             │
│  Processing audio files into dataset format...              │
│                                                             │
│  Ready to start preprocessing                               │
│                                                             │
│  Progress:                                                  │
│  [██████████░░░░░░░░░░░░░░░░░░] 33%                         │
│                                                             │
│  Files processed: 1 / 3                                     │
│                                                             │
│  Processing Log:                                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Dataset configuration loaded                        │   │
│  │ Audio files selected: 3                             │   │
│  │ Starting preprocessing...                           │   │
│  │ Dataset name: my_dataset                            │   │
│  │ Output path: /path/to/output                        │   │
│  │ Sample rate: 44100 Hz                               │   │
│  │ Processing sample1.wav...                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│                      [Start Processing] [Cancel]            │
│                                  [< Back] [Cancel] [Finish] │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. Multi-Method File Selection

Users can add audio files in three ways:

1. **Browse Folders**: Recursively scans directories for all supported audio files
2. **Add Files**: Direct file selection via file dialog
3. **Drag & Drop**: Drop folders or individual files directly into the wizard

**Supported Formats**: WAV, MP3, FLAC, OGG, AIFF, OPUS, AAC

### 2. Integrated Audio Preview

The audio player widget provides:
- **Waveform Visualization**: Real-time visual representation of audio
- **Playback Controls**: Play/pause button
- **Position Seeking**: Slider to jump to any position
- **Time Display**: Current position and total duration
- **File Information**: Sample rate and channel configuration

### 3. Smart Form Validation

The parameters page includes:
- **Required Fields**: Marked with asterisk (*)
- **Real-time Validation**: Errors shown as user types
- **Valid Characters**: Only alphanumeric, hyphens, and underscores allowed
- **Path Validation**: Checks if output directory exists
- **Directory Creation**: Offers to create missing directories
- **Next Button**: Disabled until all required fields are valid

### 4. Progress Monitoring

The preprocessing page shows:
- **Status Label**: Current operation state
- **Progress Bar**: Visual percentage indicator (0-100%)
- **File Counter**: "X files processed out of Y total"
- **Log Viewer**: Real-time processing messages with monospace font
- **Control Buttons**: Start/cancel operations

## Technical Highlights

### Architecture
- **3-Layer Separation**: UI (PyQt6) → Signals → Backend (Pure Python)
- **Signal/Slot Pattern**: Clean event-driven communication
- **Page Validation**: Built-in `isComplete()` and `validatePage()` methods
- **State Management**: Wizard tracks shared data across pages

### Code Quality
- **Type Hints**: All public methods documented with type hints
- **Docstrings**: Comprehensive documentation for all classes and methods
- **Unit Tests**: 39 tests covering all functionality
- **PEP 8 Compliant**: Black formatter ready
- **No Qt in Backend**: Audio player uses soundfile/sounddevice

### Dependencies
- **PyQt6**: Modern Qt bindings for Python
- **soundfile**: Professional audio I/O library
- **sounddevice**: Cross-platform audio playback
- **numpy**: Efficient numerical operations for waveform processing

## Usage Example

```python
from PyQt6.QtWidgets import QApplication
from rave_gui.ui.dialogs.new_dataset import NewDatasetWizard

# Create application
app = QApplication([])

# Create and show wizard
wizard = NewDatasetWizard()
result = wizard.exec()

# Handle completion
if result == QWizard.DialogCode.Accepted:
    audio_files = wizard.get_audio_files()
    config = wizard.get_dataset_config()
    
    print(f"Dataset: {config['name']}")
    print(f"Files: {len(audio_files)}")
    print(f"Output: {config['output_path']}")
    print(f"Sample Rate: {config['sample_rate']} Hz")
    print(f"Channels: {config['channels']}")
```

## Testing

### Run Unit Tests
```bash
# Test wizard
pytest tests/test_ui/test_new_dataset_wizard.py -v

# Test audio player
pytest tests/test_ui/test_audio_player.py -v

# All UI tests
pytest tests/test_ui/ -v
```

### Manual Testing
```bash
# Launch interactive test
python tests/manual_test_wizard.py
```

## Files Changed

### Modified Files
1. **rave_gui/ui/dialogs/new_dataset.py** (549 lines)
   - Expanded from skeleton to full implementation
   - Added 4 complete wizard pages
   - Integrated audio player widget

2. **rave_gui/ui/widgets/audio_player.py** (245 lines)
   - Expanded from placeholder to fully functional
   - Added waveform visualization
   - Implemented audio playback

### New Files
1. **tests/test_ui/test_new_dataset_wizard.py** - 24 unit tests
2. **tests/test_ui/test_audio_player.py** - 15 unit tests
3. **tests/manual_test_wizard.py** - Interactive test launcher
4. **docs/DATASET_WIZARD_IMPLEMENTATION.md** - Complete API documentation

## Next Steps

This wizard provides the UI foundation. To complete the feature:

1. **Backend Integration**: Connect to RAVE preprocessing subprocess
   - Create `backend/dataset.py` with `DatasetPreprocessor` class
   - Implement subprocess management for `rave preprocess` command
   - Wire up progress signals to UI

2. **Database Integration**: Save dataset metadata
   - Store dataset records in SQLite
   - Track preprocessing status
   - Link to parent project

3. **Error Handling**: Robust error management
   - Handle preprocessing failures
   - Validate audio files before processing
   - Provide recovery options

See `docs/DATASET_WIZARD_IMPLEMENTATION.md` for detailed integration guide.
