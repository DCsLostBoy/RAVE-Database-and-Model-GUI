### Issue 8: Create Export Wizard Interface

**Description:**  
Implement export wizard for model export with format selection, validation, and presets for different platforms.

**Acceptance Criteria:**  

- Export wizard guides through configuration
- Format selection (TorchScript, ONNX)
- Export presets for Max/MSP, PureData, DAW
- Validation before export
- Progress indication during export

**Files to Modify:**  

- `/rave_gui/ui/dialogs/export_model.py`
- `/rave_gui/ui/pages/export.py`

**Suggested Labels:**  

- feature
- frontend
- export

**Priority:**  

- Medium

---

### Issue 9: Implement Theme Switching UI

**Description:**  
Complete theme switching functionality with light/dark mode toggle in settings dialog.

**Acceptance Criteria:**  

- Theme switcher in settings dialog
- Themes apply without restart
- Theme preference persisted
- All UI elements respect theme

**Files to Modify:**  

- `/rave_gui/ui/dialogs/settings.py`
- `/rave_gui/resources/themes/dark.qss`
- `/rave_gui/resources/themes/light.qss`

**Suggested Labels:**  

- enhancement
- frontend
- ui

**Priority:**  

- Low

---

### Issue 10: Add Keyboard Navigation Support

**Description:**  
Implement comprehensive keyboard navigation throughout the application for accessibility.

**Acceptance Criteria:**  

- All interactive elements keyboard accessible
- Tab order logical
- Keyboard shortcuts documented
- Focus indicators visible

**Files to Modify:**  

- `/rave_gui/main_window.py`
- `/rave_gui/ui/pages/*.py`

**Suggested Labels:**  

- enhancement
- frontend
- accessibility

**Priority:**  

- Low

---

## Backend Development Issues

### Issue 11: Implement Dataset Preprocessing Wrapper

**Description:**  
Create subprocess wrapper for RAVE preprocess CLI with progress monitoring and cancellation support.

**Acceptance Criteria:**  

- Subprocess launches RAVE preprocess
- Progress parsed from output
- Cancellation works without corruption
- Error handling for failed preprocessing
- Logs captured and displayed

**Files to Modify:**  

- `/rave_gui/backend/dataset.py`
- `/rave_gui/core/process.py`

**Suggested Labels:**  

- feature
- backend
- dataset

**Priority:**  

- High

---

### Issue 12: Create Training Process Manager

**Description:**  
Implement training subprocess management with real-time monitoring, pause/resume, and queue system.

**Acceptance Criteria:**  

- Training launches in subprocess
- Real-time log monitoring
- Pause/resume functionality
- Training queue system
- Automatic restart on failure

**Files to Modify:**  

- `/rave_gui/backend/training.py`
- `/rave_gui/core/process.py`

**Suggested Labels:**  

- feature
- backend
- training

**Priority:**  

- High

---

### Issue 13: Implement Real-time Metrics Parser

**Description:**  
Create log parser that monitors RAVE training output and extracts metrics for GUI display.

**Acceptance Criteria:**  

- Metrics update within 1 second of logging
- Parser handles all RAVE metric types
- No memory leaks during long runs
- Recovers from malformed log lines

**Files to Modify:**  

- `/rave_gui/core/log_monitor.py`
- `/rave_gui/backend/training.py`

**Suggested Labels:**  

- feature
- backend
- monitoring

**Priority:**  

- High

---

### Issue 14: Build Config Composition System

**Description:**  
Implement Gin config parsing with composition support for combining multiple configs.

**Acceptance Criteria:**  

- All .gin files discovered and parsed
- Config composition (base + modifiers)
- Validation of composed configs
- Export to command-line args
- JSON serialization for database

**Files to Modify:**  

- `/rave_gui/core/config.py`

**Suggested Labels:**  

- feature
- backend
- configuration

**Priority:**  

- High

---

### Issue 15: Create Model Inference Runner

**Description:**  
Implement model loading and inference for testing with custom audio files.

**Acceptance Criteria:**  

- Models load from checkpoints
- Inference runs on uploaded audio
- Streaming mode support
- Prior model composition
- Batch inference capability

**Files to Modify:**  

- `/rave_gui/backend/model.py`

**Suggested Labels:**  

- feature
- backend
- models

**Priority:**  

- Medium

---

### Issue 16: Implement Export Process Manager

**Description:**  
Create export functionality for TorchScript and ONNX formats with validation.

**Acceptance Criteria:**  

- TorchScript export functional
- ONNX export functional
- Streaming mode toggle
- Export validation
- Prior model inclusion

**Files to Modify:**  

- `/rave_gui/backend/export.py`

**Suggested Labels:**  

- feature
- backend
- export

**Priority:**  

- Medium

---

### Issue 17: Add Memory Usage Estimator

**Description:**  
Create calculator for estimating GPU memory requirements based on model configuration.

**Acceptance Criteria:**  

- Estimates within 20% of actual usage
- Warning if >90% of available VRAM
- Recommendations for reducing usage
- Works for all model configurations

**Files to Modify:**  

- `/rave_gui/backend/training.py`
- `/rave_gui/core/utils.py`

**Suggested Labels:**  

- feature
- backend
- utility

**Priority:**  

- Low

---

## Database Issues

### Issue 18: Implement SQLite Schema

**Description:**  
Create and verify SQLite database schema for projects, datasets, experiments, models, and exports.

**Acceptance Criteria:**  

- All tables created with proper relationships
- Foreign key constraints enforced
- Indexes for performance
- Migration support for updates

**Files to Modify:**  

- `/rave_gui/core/database.py`

**Suggested Labels:**  

- feature
- backend
- database

**Priority:**  

- High

---

### Issue 19: Add Database CRUD Operations

**Description:**  
Implement complete CRUD operations for all database entities with proper error handling.

**Acceptance Criteria:**  

- Create, read, update, delete for all entities
- Transaction support for consistency
- Proper error handling
- Query optimization

**Files to Modify:**  

- `/rave_gui/core/database.py`
- `/rave_gui/backend/project.py`

**Suggested Labels:**  

- feature
- backend
- database

**Priority:**  

- High

---

## Testing Issues

### Issue 20: Write Backend Unit Tests

**Description:**  
Create comprehensive unit tests for all backend managers and core utilities.

**Acceptance Criteria:**  

- 80%+ code coverage for backend
- Tests for all public methods
- Mock subprocess calls
- Database test fixtures

**Files to Modify:**  

- `/tests/test_backend/*.py`

**Suggested Labels:**  

- testing
- backend

**Priority:**  

- Medium

---

### Issue 21: Create UI Integration Tests

**Description:**  
Implement pytest-qt tests for UI components and workflows.

**Acceptance Criteria:**  

- Test all dialogs and wizards
- Navigation flow tests
- Widget interaction tests
- Error handling tests

**Files to Modify:**  

- `/tests/test_ui/*.py`

**Suggested Labels:**  

- testing
- frontend

**Priority:**  

- Medium

---

### Issue 22: Add End-to-End Workflow Tests

**Description:**  
Create integration tests for complete workflows from dataset creation to model export.

**Acceptance Criteria:**  

- Dataset → Train → Export workflow
- Error recovery scenarios
- Performance benchmarks
- Cross-platform validation

**Files to Modify:**  

- `/tests/test_integration/*.py`

**Suggested Labels:**  

- testing
- integration

**Priority:**  

- Low

---

## Documentation Issues

### Issue 23: Create User Guide

**Description:**  
Write comprehensive user guide covering all features with screenshots and examples.

**Acceptance Criteria:**  

- Getting started section
- Feature-by-feature guide
- Screenshots for all workflows
- Troubleshooting section

**Files to Modify:**  

- `/docs/user_guide.md`
- `/docs/screenshots/`

**Suggested Labels:**  

- documentation

**Priority:**  

- Medium

---

### Issue 24: Write Installation Guide

**Description:**  
Create detailed installation guides for Windows, Mac, and Linux with dependency setup.

**Acceptance Criteria:**  

- Platform-specific instructions
- Virtual environment setup
- CUDA configuration for GPU
- Common issues and solutions

**Files to Modify:**  

- `/docs/installation.md`
- `/README.md`

**Suggested Labels:**  

- documentation

**Priority:**  

- High

---

### Issue 25: Create API Reference

**Description:**  
Document internal APIs for plugin development and extensions.

**Acceptance Criteria:**  

- All public APIs documented
- Code examples included
- Plugin development guide
- Type hints documented

**Files to Modify:**  

- `/docs/api_reference.md`
- `/docs/developer_guide.md`

**Suggested Labels:**  

- documentation

**Priority:**  

- Low

---

## DevOps Issues

### Issue 26: Create PyInstaller Build Configuration

**Description:**  
Set up PyInstaller configuration for creating standalone executables on all platforms.

**Acceptance Criteria:**  

- Windows .exe builds successfully
- Mac .app bundle works
- Linux AppImage created
- All dependencies included

**Files to Modify:**  

- `/build.spec`
- `/.github/workflows/build.yml`

**Suggested Labels:**  

- devops
- deployment

**Priority:**  

- Medium

---

### Issue 27: Set Up CI/CD Pipeline

**Description:**  
Implement GitHub Actions workflow for automated testing and building.

**Acceptance Criteria:**  

- Tests run on PR
- Code formatting checked
- Coverage reports generated
- Artifacts uploaded

**Files to Modify:**  

- `/.github/workflows/test.yml`
- `/.github/workflows/release.yml`

**Suggested Labels:**  

- devops
- ci-cd

**Priority:**  

- Medium

---

### Issue 28: Create Release Automation

**Description:**  
Automate release process with version tagging and changelog generation.

**Acceptance Criteria:**  

- Semantic versioning
- Automatic changelog
- GitHub releases created
- Download links updated

**Files to Modify:**  

- `/.github/workflows/release.yml`
- `/scripts/release.py`

**Suggested Labels:**  

- devops
- automation

**Priority:**  

- Low

---

## Bug Fixes

### Issue 29: Fix Import Errors in Current Implementation

**Description:**  
Resolve PyQt6 import errors noted in Epic 1 completion summary.

**Acceptance Criteria:**  

- All imports resolve correctly
- Virtual environment setup documented
- Requirements.txt verified complete

**Files to Modify:**  

- `/requirements.txt`
- `/setup.py`

**Suggested Labels:**  

- bug
- setup

**Priority:**  

- High

---

### Issue 30: Fix Config Parser for Complex Gin Files

**Description:**  
Enhance simplified Gin parser to handle complex configurations as noted in limitations.

**Acceptance Criteria:**  

- Nested imports handled
- All config parameters extracted
- Validation for complex compositions

**Files to Modify:**  

- `/rave_gui/core/config.py`

**Suggested Labels:**  

- bug
- backend

**Priority:**  

- Medium

---

## Performance Issues

### Issue 31: Optimize UI Rendering for Large Datasets

**Description:**  
Implement lazy loading and pagination for dataset lists to prevent UI lag.

**Acceptance Criteria:**  

- Lists load incrementally
- Virtual scrolling for large lists
- Search without full reload
- <100ms response time

**Files to Modify:**  

- `/rave_gui/ui/pages/datasets.py`
- `/rave_gui/ui/widgets/dataset_table.py`

**Suggested Labels:**  

- enhancement
- performance
- frontend

**Priority:**  

- Medium

---

### Issue 32: Optimize Memory Usage During Training

**Description:**  
Implement efficient log buffering and metrics storage to prevent memory growth.

**Acceptance Criteria:**  

- Log buffer with size limit
- Metrics downsampling for plots
- Old data purged periodically
- <2GB memory during training

**Files to Modify:**  

- `/rave_gui/core/log_monitor.py`
- `/rave_gui/ui/widgets/metrics_plot.py`

**Suggested Labels:**  

- enhancement
- performance
- backend

**Priority:**  

- Low

---

## Feature Enhancements

### Issue 33: Add Dataset Augmentation Options

**Description:**  
Implement data augmentation controls in dataset wizard (mute, compress, gain).

**Acceptance Criteria:**  

- Augmentation checkboxes in wizard
- Preview of augmented audio
- Parameters adjustable
- Saved with dataset config

**Files to Modify:**  

- `/rave_gui/ui/dialogs/new_dataset.py`
- `/rave_gui/backend/dataset.py`

**Suggested Labels:**  

- enhancement
- feature
- dataset

**Priority:**  

- Low

---

### Issue 34: Implement Training Templates

**Description:**  
Create system for saving and loading training configuration templates.

**Acceptance Criteria:**  

- Save current config as template
- Load template in wizard
- Share templates between projects
- Default templates included

**Files to Modify:**  

- `/rave_gui/ui/dialogs/new_training.py`
- `/rave_gui/resources/templates/`

**Suggested Labels:**  

- enhancement
- feature
- training

**Priority:**  

- Low

---

### Issue 35: Add Batch Dataset Processing

**Description:**  
Enable preprocessing multiple datasets in queue with batch configuration.

**Acceptance Criteria:**  

- Queue multiple preprocessing jobs
- Apply same config to multiple inputs
- Progress for entire queue
- Error recovery per job

**Files to Modify:**  

- `/rave_gui/backend/dataset.py`
- `/rave_gui/ui/dialogs/batch_preprocess.py`

**Suggested Labels:**  

- enhancement
- feature
- dataset

**Priority:**  

- Low

---

### Issue 36: Create Model Comparison Tool

**Description:**  
Build side-by-side model comparison with metrics, configs, and audio results.

**Acceptance Criteria:**  

- Compare 2-4 models simultaneously
- Show config differences
- Plot metrics together
- A/B audio testing

**Files to Modify:**  

- `/rave_gui/ui/dialogs/compare_models.py`
- `/rave_gui/ui/widgets/comparison_view.py`

**Suggested Labels:**  

- enhancement
- feature
- models

**Priority:**  

- Low

---

### Issue 37: Add Cloud Storage Integration

**Description:**  
Implement cloud storage support for datasets and models (S3, Google Drive).

**Acceptance Criteria:**  

- Configure cloud credentials
- Upload/download datasets
- Sync trained models
- Progress indication

**Files to Modify:**  

- `/rave_gui/backend/cloud.py`
- `/rave_gui/ui/dialogs/cloud_settings.py`

**Suggested Labels:**  

- enhancement
- feature
- future

**Priority:**  

- Low

---

## Critical Path Issues

### Issue 38: Complete Sprint 1 Application Shell

**Description:**  
Finalize application shell with all Sprint 1 tasks from Week 1 backlog.

**Acceptance Criteria:**  

- Project structure finalized
- Main window with navigation
- Page routing functional
- Settings dialog complete
- Theme system working
- Status bar notifications

**Files to Modify:**  

- `/rave_gui/app.py`
- `/rave_gui/main_window.py`

**Suggested Labels:**  

- critical-path
- sprint-1

**Priority:**  

- High

---

### Issue 39: Complete Sprint 2 Project Management

**Description:**  
Implement complete project management system per Week 2 backlog.

**Acceptance Criteria:**  

- Database schema implemented
- Project CRUD operations
- Project selector dialog
- Recent projects list
- Import/export projects

**Files to Modify:**  

- `/rave_gui/backend/project.py`
- `/rave_gui/ui/dialogs/project_selector.py`

**Suggested Labels:**  

- critical-path
- sprint-2

**Priority:**  

- High

---

### Issue 40: Complete Sprint 3 Dataset Wizard

**Description:**  
Build complete dataset wizard framework per Week 3 backlog.

**Acceptance Criteria:**  

- Wizard framework created
- File browser with audio support
- Audio preview/playback
- Parameter configuration
- Form validation
- Drag-and-drop support

**Files to Modify:**  

- `/rave_gui/ui/dialogs/new_dataset.py`
- `/rave_gui/ui/widgets/audio_player.py`

**Suggested Labels:**  

- critical-path
- sprint-3

**Priority:**  

- High

---

### Issue 41: Complete Sprint 4 Dataset Processing

**Description:**  
Implement dataset processing backend per Week 4 backlog.

**Acceptance Criteria:**  

- Subprocess wrapper functional
- Progress monitoring works
- Log viewer displays output
- Cancellation implemented
- Dataset list view complete

**Files to Modify:**  

- `/rave_gui/backend/dataset.py`
- `/rave_gui/ui/pages/datasets.py`

**Suggested Labels:**  

- critical-path
- sprint-4

**Priority:**  

- High

---

## Quick Win Issues

### Issue 42: Add Dark Theme Toggle

**Description:**  
Quick win - implement dark theme toggle button in toolbar.

**Acceptance Criteria:**  

- Toggle button in main window
- Instant theme switching
- State persisted

**Files to Modify:**  

- `/rave_gui/main_window.py`

**Suggested Labels:**  

- quick-win
- enhancement

**Priority:**  

- Low

---

### Issue 43: Add Drag & Drop for Audio Files

**Description:**  
Quick win - enable drag & drop for audio file selection.

**Acceptance Criteria:**  

- Files draggable to dataset wizard
- Multiple files supported
- Visual feedback during drag

**Files to Modify:**  

- `/rave_gui/ui/dialogs/new_dataset.py`

**Suggested Labels:**  

- quick-win
- enhancement

**Priority:**  

- Low

---

### Issue 44: Add Audio Preview Button

**Description:**  
Quick win - add preview button for audio files in dataset wizard.

**Acceptance Criteria:**  

- Play button for each file
- Stop/pause controls
- Duration display

**Files to Modify:**  

- `/rave_gui/ui/widgets/audio_player.py`

**Suggested Labels:**  

- quick-win
- enhancement

**Priority:**  

- Low

---

### Issue 45: Add Progress Bars Everywhere

**Description:**  
Quick win - add progress bars to all long operations.

**Acceptance Criteria:**  

- Progress bars for all operations >1s
- Indeterminate for unknown duration
- Cancel button where applicable

**Files to Modify:**  

- `/rave_gui/ui/widgets/progress_dialog.py`

**Suggested Labels:**  

- quick-win
- enhancement

**Priority:**  

- Low

---

### Issue 46: Add Recent Projects Menu

**Description:**  
Quick win - add recent projects to File menu.

**Acceptance Criteria:**  

- Last 5 projects in menu
- Clear recent option
- Project paths shown

**Files to Modify:**  

- `/rave_gui/main_window.py`
- `/rave_gui/core/settings.py`

**Suggested Labels:**  

- quick-win
- enhancement

**Priority:**  

- Low

---

### Issue 47: Add Keyboard Shortcuts

**Description:**  
Quick win - implement common keyboard shortcuts.

**Acceptance Criteria:**  

- Ctrl+N for new project
- Ctrl+O for open project
- F5 for refresh
- Documented in help menu

**Files to Modify:**  

- `/rave_gui/main_window.py`

**Suggested Labels:**  

- quick-win
- enhancement

**Priority:**  

- Low
