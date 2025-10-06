"""
Training process wrapper with Qt signals.
"""
import re
from typing import Optional, Dict
from PyQt6.QtCore import pyqtSignal
from rave_gui.core.process import ProcessThread


class TrainingProcess(ProcessThread):
    """Thread for running RAVE training with metrics parsing."""
    
    metrics_update = pyqtSignal(dict)  # Parsed metrics from logs
    step_update = pyqtSignal(int, int)  # current_step, total_steps
    
    def __init__(self, command: list, training_config: Dict):
        """Initialize training process.
        
        Args:
            command: Command list for subprocess
            training_config: Training configuration dictionary
        """
        super().__init__(command)
        self.training_config = training_config
        
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
