# Epic #1 - Core GUI Infrastructure Testing Guide

## Overview

This document provides a comprehensive testing guide for verifying all acceptance criteria of Epic #1: Core GUI Infrastructure.

## Prerequisites

Before testing, ensure you have the required dependencies installed:

```bash
pip install PyQt6 pytest pytest-qt
```

## Automated Verification

Run the automated verification script that tests all backend components:

```bash
python verify_epic1.py
```

This script verifies:
- ✅ Settings persistence (themes, paths, window geometry, recent projects)
- ✅ Configuration parsing and composition
- ✅ Database schema and project management
- ✅ Module imports and structure

## Manual GUI Testing

### 1. Application Launch

Test that the application launches successfully:

```bash
python -m rave_gui.app
```

**Expected Results:**
- Application window opens without errors
- Window size is 80% of screen or restored from last session
- Dark theme is applied by default (or last selected theme)
- Project selector dialog appears on first launch

### 2. Project Management

#### Create New Project

1. Click `File > New Project...` or use `Ctrl+N`
2. Enter project name: "Test Project 1"
3. Click "Browse..." and select a directory
4. Click "OK"

**Expected Results:**
- Project is created successfully
- Window title updates to "RAVE GUI - Test Project 1"
- Status bar shows "Project 'Test Project 1' created successfully"
- Project directory is created on disk

#### Switch Projects

1. Click `File > Switch Project...` or use `Ctrl+O`
2. Create another project: "Test Project 2"
3. Select "Test Project 1" from the list
4. Click "OK"

**Expected Results:**
- Window title updates to "RAVE GUI - Test Project 1"
- Status bar shows "Switched to project: Test Project 1"
- Last project is saved in settings

#### Delete Project

1. Open project selector (`File > Switch Project...`)
2. Select a project from the list
3. Click "Delete Project"
4. Confirm deletion

**Expected Results:**
- Confirmation dialog appears
- Project is removed from database (files remain on disk)
- Project list updates

### 3. Configuration Management

The ConfigManager works in the background to parse RAVE .gin files. You can verify it programmatically:

```python
from rave_gui.core.config import ConfigManager

cm = ConfigManager()
print("Available configs:", cm.list_configs())
print("Categories:", cm.get_config_categories())

# Test composition
if "v2" in cm.list_configs() and "causal" in cm.list_configs():
    composed = cm.compose_configs(["v2", "causal"])
    print("Composed config:", composed)
```

**Expected Results:**
- All .gin files in rave/configs/ are discovered
- Configs are categorized into "base" and "modifiers"
- Config composition merges parameters correctly

### 4. Navigation System

Test navigation between all sections:

1. Click "Dashboard" in the sidebar → Dashboard page appears
2. Click "Datasets" → Datasets page appears
3. Click "Training" → Training page appears
4. Click "Models" → Models page appears
5. Click "Export" → Export page appears

**Expected Results:**
- Page switching is smooth and fast (<100ms)
- Selected button is highlighted
- Page content changes appropriately
- No errors in console

### 5. Theme Switching

1. Click `Edit > Settings...` or use `Ctrl+,`
2. Change theme from "Dark" to "Light"
3. Click "OK"

**Expected Results:**
- Theme changes immediately without restart
- Status bar shows "Theme changed to light"
- Theme selection persists across sessions

Test theme persistence:
1. Close application
2. Reopen application
3. Verify light theme is still applied

### 6. Settings Persistence

Test that all settings persist across sessions:

#### Window Geometry
1. Resize and move the window
2. Close application
3. Reopen application
4. Window should restore to previous size and position

#### Last Project
1. Create/select a project
2. Close application
3. Reopen application
4. Same project should be loaded automatically

#### Default Paths
1. Open settings (`Edit > Settings...`)
2. Set custom default paths for datasets and models
3. Click "OK"
4. Close and reopen application
5. Open settings again
6. Paths should be preserved

#### Recent Projects
Recent projects are tracked automatically. The last 10 projects are kept in order of use.

### 7. Cross-Platform Testing

Test on multiple platforms if available:

- **Windows**: Test with Windows 10/11
- **macOS**: Test with macOS 10.15+
- **Linux**: Test with Ubuntu 20.04+ or similar

**Platform-Specific Checks:**
- High-DPI scaling works correctly
- Window decorations render properly
- File dialogs use native style
- Keyboard shortcuts work (Ctrl on Windows/Linux, Cmd on Mac)

## Automated Tests

Run the test suite:

```bash
# Run all tests
pytest tests/

# Run only backend tests
pytest tests/test_backend/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_backend/test_project_manager.py
```

**Test Coverage:**
- `test_project_manager.py`: 10 tests for project CRUD operations
- `test_config_manager.py`: 8 tests for config parsing and composition
- `test_main_window.py`: UI navigation and component tests

## Acceptance Criteria Checklist

- [ ] **Application launches successfully on Windows/Mac/Linux**
  - Test on at least one platform
  - No errors or exceptions on startup
  - Window appears with correct size and theme

- [ ] **Users can create and switch between projects**
  - New project dialog works
  - Projects are saved to database
  - Project selector shows all projects
  - Switching updates window title and status
  - Project deletion works with confirmation

- [ ] **All Gin configs parsed and accessible**
  - ConfigManager finds rave/configs/ directory
  - All .gin files are discovered
  - Config parsing extracts parameters correctly
  - Config composition works (base + modifiers)

- [ ] **Navigation works smoothly between all sections**
  - All 5 pages accessible (Dashboard, Datasets, Training, Models, Export)
  - Page switching is fast (<100ms)
  - Sidebar buttons highlight correctly
  - No visual glitches

- [ ] **Theme switching functional**
  - Settings dialog shows theme options
  - Changing theme updates UI immediately
  - Both dark and light themes work
  - Theme persists across sessions

- [ ] **Settings persistence working**
  - Window geometry saves and restores
  - Last project loads on startup
  - Theme preference persists
  - Default paths persist
  - Recent projects tracked
  - Settings survive app restart

## Known Limitations

1. **Page Content**: The Dashboard, Datasets, Training, Models, and Export pages are placeholder implementations. Full functionality will be added in later Epics.

2. **Config Parsing**: The Gin config parser is simplified and may not handle all edge cases. Complex nested configs might need manual verification.

3. **Error Handling**: While basic error handling is in place, some edge cases (network issues, corrupted database, etc.) may need additional handling.

## Troubleshooting

### Application won't start
- Ensure PyQt6 is installed: `pip install PyQt6`
- Check Python version (3.8+ required)
- Look for error messages in console

### Theme not loading
- Verify theme files exist: `rave_gui/resources/themes/dark.qss` and `light.qss`
- Check settings file: `~/.rave_gui/settings.json`
- Try deleting settings file to reset

### Database errors
- Check database file: `~/.rave_gui/rave_gui.db`
- Ensure directory is writable
- Delete database to reset (will lose projects)

### Config parsing issues
- Verify RAVE is installed: `pip install acids-rave`
- Check if configs exist: Look for `rave/configs/` in Python site-packages
- Run ConfigManager tests: `pytest tests/test_backend/test_config_manager.py`

## Next Steps

After completing Epic #1 verification:

1. Review any issues found during testing
2. Document any platform-specific quirks
3. Proceed to Epic #2: Dataset Management Module
4. Keep Epic #1 infrastructure stable during future development

## Reporting Issues

When reporting issues, include:
- Platform (Windows/Mac/Linux) and version
- Python version
- PyQt6 version
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if relevant
- Console output or error messages
