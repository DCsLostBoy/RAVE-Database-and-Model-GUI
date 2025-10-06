"""
Logging utilities for RAVE GUI.
"""
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(name: str, log_file: Optional[Path] = None, 
                level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with console and optional file output.
    
    Args:
        name: Logger name
        log_file: Optional path to log file
        level: Logging level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
    
    return logger


class LogMonitor:
    """Monitor log files for changes and parse new content."""
    
    def __init__(self, log_path: Path):
        """Initialize the log monitor.
        
        Args:
            log_path: Path to log file to monitor
        """
        self.log_path = log_path
        self.last_position = 0
        
    def get_new_lines(self) -> list[str]:
        """Get new lines added to the log file.
        
        Returns:
            List of new lines
        """
        new_lines = []
        
        if not self.log_path.exists():
            return new_lines
        
        with open(self.log_path, 'r') as f:
            # Seek to last read position
            f.seek(self.last_position)
            
            # Read new lines
            new_lines = f.readlines()
            
            # Update position
            self.last_position = f.tell()
        
        return new_lines
    
    def parse_metrics(self, lines: list[str]) -> dict:
        """Parse training metrics from log lines.
        
        Args:
            lines: Log lines to parse
            
        Returns:
            Dictionary of parsed metrics
        """
        metrics = {}
        
        # TODO: Implement metric parsing based on PyTorch Lightning log format
        # Look for patterns like:
        # - "Epoch X: loss=Y.YY"
        # - "Step X/Y"
        # - "Learning rate: X.XXe-X"
        
        return metrics
