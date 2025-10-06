"""
Training management backend.
"""
import json
import re
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from PyQt6.QtCore import pyqtSignal
from rave_gui.core.process import ProcessThread, RAVEProcess


class TrainingProcess(ProcessThread):
    """Thread for running RAVE training with metrics parsing."""
    
    metrics_update = pyqtSignal(dict)  # Parsed metrics from logs
    step_update = pyqtSignal(int, int)  # current_step, total_steps
    
    def __init__(self, config: Dict):
        """Initialize training process.
        
        Args:
            config: Training configuration containing:
                - dataset_path: Path to dataset
                - name: Training run name
                - config: RAVE config name
                - overrides: Optional list of config overrides
        """
        self.training_config = config
        
        # Get dataset path
        dataset_path = Path(config['dataset_path'])
        
        # Build training command
        overrides = config.get('overrides', [])
        if config.get('max_steps'):
            overrides.append(f"PHASE.max_steps={config['max_steps']}")
        
        command = RAVEProcess.train(
            config=config.get('config', 'v2'),
            db_path=dataset_path,
            name=config['name'],
            overrides=overrides if overrides else None
        )
        
        super().__init__(command)
        
        # Metrics patterns for parsing
        self.metric_patterns = {
            'loss': re.compile(r'loss[:\s]+([0-9.]+)', re.IGNORECASE),
            'step': re.compile(r'step[:\s]+(\d+)', re.IGNORECASE),
            'epoch': re.compile(r'epoch[:\s]+(\d+)', re.IGNORECASE),
            'lr': re.compile(r'lr[:\s]+([0-9.e-]+)', re.IGNORECASE),
            'val_loss': re.compile(r'val[_\s]loss[:\s]+([0-9.]+)', re.IGNORECASE),
        }
        
        self.current_metrics = {}
    
    def parse_progress(self, line: str) -> tuple[Optional[int], str]:
        """Parse training progress from log line.
        
        Args:
            line: Log line
            
        Returns:
            Tuple of (percentage, message) or (None, line)
        """
        # Parse metrics from the line
        metrics = {}
        for name, pattern in self.metric_patterns.items():
            match = pattern.search(line)
            if match:
                try:
                    value = float(match.group(1))
                    metrics[name] = value
                except (ValueError, IndexError):
                    pass
        
        # Update current metrics and emit signal if we found any
        if metrics:
            self.current_metrics.update(metrics)
            self.metrics_update.emit(metrics)
            
            # If we have step info, emit step update
            if 'step' in metrics:
                step = int(metrics['step'])
                # Estimate total steps if max_steps was provided
                total = self.training_config.get('max_steps', 500000)
                self.step_update.emit(step, total)
                
                # Calculate progress percentage
                progress = int((step / total) * 100) if total > 0 else 0
                return progress, f"Step {step}/{total}"
        
        return None, line


class TrainingManager:
    """Manages model training operations."""
    
    def __init__(self, db_connection):
        """Initialize the training manager.
        
        Args:
            db_connection: Database connection object
        """
        self.db = db_connection
        self.active_processes = {}  # experiment_id -> TrainingProcess
        
    def start_training(self, config: Dict) -> int:
        """Start a new training run.
        
        Args:
            config: Training configuration dictionary containing:
                - name: Training run name
                - dataset_id: Dataset ID to train on
                - project_id: Project ID (optional)
                - config: RAVE config name (e.g., 'v2')
                - overrides: List of config overrides (optional)
                - max_steps: Maximum training steps (optional)
            
        Returns:
            Experiment ID
        """
        # Create experiment record in database
        cursor = self.db.execute(
            """INSERT INTO experiments 
               (project_id, name, dataset_id, config, status, started_at, metrics)
               VALUES (?, ?, ?, ?, 'running', ?, ?)""",
            (
                config.get('project_id'),
                config['name'],
                config['dataset_id'],
                json.dumps(config),
                datetime.now().isoformat(),
                json.dumps({})
            )
        )
        experiment_id = cursor.lastrowid
        return experiment_id
    
    def update_experiment_status(self, experiment_id: int, status: str, 
                                 completed_at: Optional[str] = None):
        """Update experiment status.
        
        Args:
            experiment_id: Experiment ID
            status: New status ('running', 'completed', 'failed', 'stopped')
            completed_at: Completion timestamp (optional)
        """
        if completed_at:
            self.db.execute(
                "UPDATE experiments SET status = ?, completed_at = ? WHERE id = ?",
                (status, completed_at, experiment_id)
            )
        else:
            self.db.execute(
                "UPDATE experiments SET status = ? WHERE id = ?",
                (status, experiment_id)
            )
    
    def update_training_metrics(self, experiment_id: int, metrics: Dict):
        """Update training metrics for an experiment.
        
        Args:
            experiment_id: Experiment ID
            metrics: Metrics dictionary
        """
        self.db.execute(
            "UPDATE experiments SET metrics = ? WHERE id = ?",
            (json.dumps(metrics), experiment_id)
        )
    
    def get_experiment(self, experiment_id: int) -> Optional[Dict]:
        """Get experiment by ID.
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Experiment dictionary or None
        """
        result = self.db.fetch_one(
            "SELECT * FROM experiments WHERE id = ?",
            (experiment_id,)
        )
        if result:
            # Parse JSON fields
            if result.get('config'):
                result['config'] = json.loads(result['config'])
            if result.get('metrics'):
                result['metrics'] = json.loads(result['metrics'])
        return result
    
    def list_experiments(self, project_id: Optional[int] = None) -> List[Dict]:
        """List all experiments, optionally filtered by project.
        
        Args:
            project_id: Optional project ID to filter by
            
        Returns:
            List of experiment dictionaries
        """
        if project_id:
            results = self.db.fetch_all(
                "SELECT * FROM experiments WHERE project_id = ? ORDER BY started_at DESC",
                (project_id,)
            )
        else:
            results = self.db.fetch_all(
                "SELECT * FROM experiments ORDER BY started_at DESC"
            )
        
        # Parse JSON fields for each result
        for result in results:
            if result.get('config'):
                result['config'] = json.loads(result['config'])
            if result.get('metrics'):
                result['metrics'] = json.loads(result['metrics'])
        
        return results
    
    def stop_training(self, experiment_id: int) -> bool:
        """Stop a running training process.
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            True if successful
        """
        if experiment_id in self.active_processes:
            process = self.active_processes[experiment_id]
            process.stop()
            self.update_experiment_status(
                experiment_id, 
                'stopped', 
                datetime.now().isoformat()
            )
            del self.active_processes[experiment_id]
            return True
        return False
    
    def get_training_metrics(self, experiment_id: int) -> Dict:
        """Get training metrics for an experiment.
        
        Args:
            experiment_id: Experiment ID
            
        Returns:
            Metrics dictionary
        """
        experiment = self.get_experiment(experiment_id)
        if experiment and experiment.get('metrics'):
            return experiment['metrics']
        return {}
    
    def register_process(self, experiment_id: int, process):
        """Register an active training process.
        
        Args:
            experiment_id: Experiment ID
            process: TrainingProcess instance
        """
        self.active_processes[experiment_id] = process
    
    def unregister_process(self, experiment_id: int):
        """Unregister a training process.
        
        Args:
            experiment_id: Experiment ID
        """
        if experiment_id in self.active_processes:
            del self.active_processes[experiment_id]
