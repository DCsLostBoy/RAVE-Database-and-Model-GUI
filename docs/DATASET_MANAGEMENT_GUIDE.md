# Dataset Management Guide

This guide explains how to use the Dataset Management features in RAVE GUI (Epic #2).

## Overview

The Dataset Management Module provides a complete workflow for:
- Creating preprocessed audio datasets for RAVE training
- Managing dataset metadata
- Browsing and organizing datasets
- Monitoring preprocessing progress in real-time

## Creating a New Dataset

### Step 1: Open the Dataset Creation Wizard

1. Navigate to the **Datasets** page from the sidebar
2. Click the **"New Dataset"** button in the top-right corner
3. The Dataset Creation Wizard will open

### Step 2: Introduction

The introduction page explains what datasets are and what the preprocessing step does:
- Converts audio files to the specified format
- Resamples to the target sample rate
- Splits audio into fixed-length chunks
- Stores data in an LMDB database for efficient training

Click **"Next"** to continue.

### Step 3: Select Audio Files

1. **Input Folder**: Click "Browse..." to select the folder containing your audio files
   - RAVE will recursively scan this folder for audio files
   - Supported formats: WAV, MP3, FLAC, OGG, etc.

2. **Output Folder**: Click "Browse..." to select where the preprocessed dataset will be stored
   - This will contain the LMDB database files
   - Ensure you have sufficient disk space (preprocessed datasets can be large)

Click **"Next"** when both paths are selected.

### Step 4: Configure Parameters

Configure the preprocessing parameters:

- **Dataset Name** (required): A unique name for your dataset (e.g., "piano_samples")
- **Sample Rate**: Target sample rate in Hz (default: 44100)
  - Common values: 44100 (CD quality), 48000 (professional), 22050 (lower quality)
- **Channels**: Number of audio channels (default: 1)
  - 1 = Mono, 2 = Stereo
- **Samples per Chunk**: Number of audio samples per chunk (default: 65536)
  - Larger values = more context but more memory usage
  - Typical range: 16384 to 131072
- **Use lazy loading**: Enable for very large datasets
  - Data is loaded on-demand during training
  - Slower training but uses less memory

Click **"Next"** to start preprocessing.

### Step 5: Preprocessing

The final page shows real-time preprocessing progress:

- **Progress Bar**: Visual indication of completion percentage
- **Status Message**: Current operation status
- **Log Viewer**: Real-time output from the RAVE preprocessing command

The preprocessing operation runs in a background thread, so the UI remains responsive.

**Note**: Preprocessing can take several minutes to hours depending on:
- Amount of audio data
- Your computer's performance
- Selected parameters

When preprocessing completes:
- Click **"Finish"** to close the wizard
- The dataset will appear in the datasets table
- A status message confirms successful creation

## Managing Datasets

### Datasets Table

The main Datasets page displays all your datasets in a table:

| Column | Description |
|--------|-------------|
| **Name** | Dataset name |
| **Samples** | Number of audio samples (chunks) |
| **Duration** | Total duration in seconds |
| **Channels** | Number of audio channels |
| **Sample Rate** | Sampling rate in Hz |
| **Created** | Creation timestamp |

### Refreshing the List

Click the **"Refresh"** button to reload the datasets from the database.

The list automatically refreshes when:
- A new dataset is created
- A dataset is deleted
- The active project changes

### Selecting a Dataset

Click on any row to select a dataset. This enables the **"Delete Dataset"** button.

### Deleting a Dataset

**Method 1: Delete Button**
1. Select a dataset in the table
2. Click the **"Delete Dataset"** button at the bottom
3. Confirm the deletion in the dialog

**Method 2: Context Menu**
1. Right-click on a dataset row
2. Select **"Delete Dataset"** from the menu
3. Confirm the deletion in the dialog

**Important Notes:**
- Deleting a dataset removes its metadata from the database
- The actual dataset files on disk are **NOT** deleted
- This operation cannot be undone (in the database)
- To fully remove a dataset, manually delete the output folder

## Dataset Statistics

Each dataset's statistics are calculated and displayed:

- **Total Samples**: Number of preprocessed audio chunks
- **Duration**: Total audio duration calculated from samples and sample rate
- **Channels**: Mono (1) or Stereo (2+)
- **Sample Rate**: Audio sampling frequency

## Integration with Projects

Datasets can be associated with projects:
- When you create a dataset, it can be linked to the current project
- Use project filtering to show only datasets for a specific project
- Switching projects automatically refreshes the datasets list

## Technical Details

### Database Schema

Datasets are stored in the `datasets` table:

```sql
CREATE TABLE datasets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    num_samples INTEGER,
    channels INTEGER,
    sample_rate INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
)
```

### RAVE Preprocessing Command

The wizard builds and executes this command:

```bash
rave preprocess \
  --input_path <input_folder> \
  --output_path <output_folder> \
  --sampling_rate <sample_rate> \
  --channels <channels> \
  --num_signal <samples_per_chunk> \
  [--lazy]
```

### Architecture

The Dataset Management Module follows the 3-layer architecture:

1. **Backend** (`backend/dataset.py`): Pure Python `DatasetManager` class
   - CRUD operations for datasets
   - Statistics calculation
   - No PyQt6 dependencies

2. **Signals** (`core/signals.py`): Cross-component communication
   - `dataset_created(dataset_id, name)`
   - `dataset_deleted(dataset_id)`
   - `dataset_preprocessing_progress(dataset_id, percentage, message)`

3. **UI** (`ui/pages/datasets.py`, `ui/dialogs/new_dataset.py`): PyQt6 widgets
   - DatasetsPage: Main browsing interface
   - NewDatasetWizard: 4-page creation wizard
   - Uses `ProcessThread` for async preprocessing

## Troubleshooting

### Preprocessing Fails

If preprocessing fails:
1. Check the log viewer for error messages
2. Verify input folder contains audio files
3. Ensure output folder is writable
4. Check disk space availability
5. Verify RAVE CLI is installed: `rave --help`

### Dataset Not Appearing

If a dataset doesn't appear after creation:
1. Click the **"Refresh"** button
2. Check you're viewing the correct project
3. Verify the database file hasn't been corrupted
4. Check the application logs

### Can't Delete Dataset

If you can't delete a dataset:
1. Ensure no training jobs are using it
2. Check the dataset isn't locked by another process
3. Close and reopen the application

## Next Steps

After creating datasets:
1. Navigate to the **Training** page
2. Create a new training run
3. Select your dataset from the dropdown
4. Configure training parameters
5. Start training!

## Related Documentation

- [Project Plan](PROJECT_PLAN.md) - Epic #2: Dataset Management Module
- [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md) - Week 2-3: Dataset Management
- [Technical Decisions](TECHNICAL_DECISIONS.md) - Architecture and patterns
