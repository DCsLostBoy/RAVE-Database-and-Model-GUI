# Training Management System - Architecture Diagram

## Component Interaction Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────────────────────┐   │
│  │  TrainingPage    │         │   NewTrainingWizard              │   │
│  ├──────────────────┤         ├──────────────────────────────────┤   │
│  │ - Table view     │         │ Pages:                           │   │
│  │ - Progress bars  │         │  1. DatasetSelection             │   │
│  │ - Start/Stop btns│         │  2. ConfigSelection              │   │
│  │ - Log viewer     │         │  3. TrainingParameters           │   │
│  └────────┬─────────┘         │  4. Confirmation                 │   │
│           │                   └──────────┬───────────────────────┘   │
│           │                              │                           │
│  ┌────────▼───────────────────────┐      │                           │
│  │      MetricsPlot Widget        │      │                           │
│  ├────────────────────────────────┤      │                           │
│  │ - Matplotlib canvas            │      │                           │
│  │ - Loss plot                    │      │                           │
│  │ - Learning rate plot           │      │                           │
│  │ - Navigation toolbar           │      │                           │
│  └────────────────────────────────┘      │                           │
│                                           │                           │
└───────────────────────────────────────────┼───────────────────────────┘
                                            │
                            ┌───────────────▼────────────────┐
                            │   get_config() returns dict    │
                            └───────────────┬────────────────┘
                                            │
┌───────────────────────────────────────────▼───────────────────────────┐
│                          BUSINESS LOGIC LAYER                         │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │             TrainingManager (Pure Python)                    │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ Methods:                                                     │    │
│  │  • start_training(config) → experiment_id                   │    │
│  │  • get_experiment(experiment_id) → dict                     │    │
│  │  • list_experiments(project_id?) → list[dict]               │    │
│  │  • update_experiment_status(id, status)                     │    │
│  │  • update_training_metrics(id, metrics)                     │    │
│  │  • stop_training(experiment_id) → bool                      │    │
│  │  • register_process(id, process)                            │    │
│  │                                                              │    │
│  │ State:                                                       │    │
│  │  • db: Database connection                                  │    │
│  │  • active_processes: dict[int, TrainingProcess]            │    │
│  └────────────────┬────────────────────────────────────────────┘    │
│                   │                                                  │
│                   │ creates & manages                                │
│                   │                                                  │
│  ┌────────────────▼─────────────────────────────────────────────┐   │
│  │        TrainingProcess (extends ProcessThread)               │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │ Functionality:                                               │   │
│  │  • Runs RAVE CLI in subprocess                              │   │
│  │  • Parses log output for metrics                            │   │
│  │  • Emits signals on metrics updates                         │   │
│  │                                                              │   │
│  │ Signals:                                                     │   │
│  │  • metrics_update(dict)                                     │   │
│  │  • step_update(current_step, total_steps)                   │   │
│  │  • output(line)                                             │   │
│  │  • finished(success, message)                               │   │
│  │                                                              │   │
│  │ Metric Patterns (Regex):                                    │   │
│  │  • loss: r'loss[:\s]+([0-9.]+)'                            │   │
│  │  • step: r'step[:\s]+(\d+)'                                │   │
│  │  • lr: r'lr[:\s]+([0-9.e-]+)'                              │   │
│  │  • val_loss: r'val[_\s]loss[:\s]+([0-9.]+)'               │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────────────┬───────────────────────────────┘
                                        │
                                        │ reads/writes
                                        │
┌───────────────────────────────────────▼───────────────────────────────┐
│                            DATA LAYER                                 │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    SQLite Database                           │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ experiments table:                                           │    │
│  │  • id (PK)                                                   │    │
│  │  • project_id (FK)                                          │    │
│  │  • name                                                      │    │
│  │  • dataset_id (FK)                                          │    │
│  │  • config (JSON)                                            │    │
│  │  • status (running/completed/failed/stopped)                │    │
│  │  • started_at                                               │    │
│  │  • completed_at                                             │    │
│  │  • metrics (JSON)                                           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              RAVE CLI (External Process)                     │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │ Command:                                                     │    │
│  │   rave train --config v2 --db_path /dataset --name run1    │    │
│  │                                                              │    │
│  │ Output (stdout):                                             │    │
│  │   step: 1000 loss: 0.543 lr: 0.0001 val_loss: 0.612       │    │
│  │   step: 2000 loss: 0.432 lr: 0.0001 val_loss: 0.521       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Signal Flow Diagram

```
User Action: Click "New Training"
│
├─► TrainingPage.start_new_training()
│   │
│   ├─► NewTrainingWizard.exec()
│   │   └─► Returns config dict
│   │
│   ├─► TrainingManager.start_training(config)
│   │   └─► Creates experiment in DB, returns experiment_id
│   │
│   ├─► Create TrainingProcess(config)
│   │   │
│   │   ├─► Connect signals:
│   │   │   • output → on_training_output()
│   │   │   • metrics_update → on_metrics_update()
│   │   │   • step_update → on_step_update()
│   │   │   • finished → on_training_finished()
│   │   │
│   │   └─► TrainingProcess.start()
│   │       │
│   │       ├─► Launches subprocess: rave train ...
│   │       │
│   │       └─► Reads output line by line
│   │           │
│   │           ├─► Parses metrics with regex
│   │           │
│   │           ├─► Emits: metrics_update(dict)
│   │           │   │
│   │           │   └─► TrainingPage.on_metrics_update()
│   │           │       │
│   │           │       ├─► Updates database
│   │           │       └─► Updates MetricsPlot
│   │           │
│   │           ├─► Emits: step_update(current, total)
│   │           │   │
│   │           │   └─► TrainingPage.on_step_update()
│   │           │       └─► Updates progress bar
│   │           │
│   │           └─► Emits: output(line)
│   │               │
│   │               └─► TrainingPage.on_training_output()
│   │                   └─► Appends to log viewer
│   │
│   └─► AppSignals.training_started.emit()
│
Training completes:
│
├─► TrainingProcess emits: finished(success, message)
│   │
│   └─► TrainingPage.on_training_finished()
│       │
│       ├─► Updates experiment status in DB
│       ├─► Unregisters process
│       ├─► Emits: AppSignals.training_completed
│       └─► Refreshes experiments table
```

## Data Flow

```
Configuration Input:
┌─────────────────────────────────┐
│ NewTrainingWizard               │
├─────────────────────────────────┤
│ • Dataset ID & Path             │
│ • RAVE Config (v2)              │
│ • Modifiers (causal, snake)     │
│ • Name                          │
│ • Max Steps                     │
│ • Batch Size                    │
│ • Learning Rate                 │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ TrainingManager                 │
│ start_training(config)          │
├─────────────────────────────────┤
│ INSERT INTO experiments (...)   │
│ VALUES (config as JSON)         │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ TrainingProcess                 │
├─────────────────────────────────┤
│ cmd = ["rave", "train",         │
│        "--config", "v2",        │
│        "--db_path", path,       │
│        "--name", name]          │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ RAVE CLI (subprocess)           │
└────────────┬────────────────────┘
             │
             │ (stdout lines)
             │
             ▼
┌─────────────────────────────────┐
│ TrainingProcess.parse_progress()│
├─────────────────────────────────┤
│ Regex matching:                 │
│ "step: 1000 loss: 0.543"       │
│ → {step: 1000, loss: 0.543}    │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ Signal: metrics_update(metrics) │
└────────────┬────────────────────┘
             │
             ├─► TrainingManager.update_training_metrics()
             │   │
             │   └─► UPDATE experiments SET metrics = JSON
             │
             └─► MetricsPlot.update_metrics()
                 │
                 └─► Appends to history, redraws plots
```

## Class Relationships

```
Database ──────┐
               │
               ├──► TrainingManager
               │    │
               │    ├── active_processes: dict[int, TrainingProcess]
               │    │
               │    └──► TrainingProcess extends ProcessThread
               │         │
               │         ├── config: dict
               │         ├── metric_patterns: dict[str, Pattern]
               │         ├── current_metrics: dict
               │         │
               │         └── Signals:
               │             • metrics_update
               │             • step_update
               │
               └──► TrainingPage(QWidget)
                    │
                    ├── training_manager: TrainingManager
                    ├── experiments_table: QTableWidget
                    ├── metrics_plot: MetricsPlot
                    ├── log_viewer: QTextEdit
                    ├── progress_bar: QProgressBar
                    │
                    └── Connects to:
                        • AppSignals
                        • TrainingProcess signals
```
