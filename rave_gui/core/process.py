"""
Subprocess management for RAVE CLI operations.
"""
import subprocess
from pathlib import Path
from typing import List, Optional, Callable
from PyQt6.QtCore import QThread, pyqtSignal


class ProcessThread(QThread):
    """Thread for running subprocess operations without blocking the UI."""
    
    output = pyqtSignal(str)  # stdout/stderr output
    progress = pyqtSignal(int, str)  # percentage, message
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, command: List[str], cwd: Optional[Path] = None):
        """Initialize the process thread.
        
        Args:
            command: Command and arguments as list
            cwd: Working directory for the process
        """
        super().__init__()
        self.command = command
        self.cwd = cwd
        self.process = None
        self._should_stop = False
        
    def run(self):
        """Run the subprocess."""
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=str(self.cwd) if self.cwd else None
            )
            
            # Read output line by line
            for line in self.process.stdout:
                if self._should_stop:
                    self.process.terminate()
                    break
                    
                self.output.emit(line.strip())
                
                # Parse progress if possible
                progress, msg = self.parse_progress(line)
                if progress is not None:
                    self.progress.emit(progress, msg)
            
            # Wait for process to complete
            return_code = self.process.wait()
            success = return_code == 0
            
            message = "Completed successfully" if success else f"Failed with code {return_code}"
            self.finished.emit(success, message)
            
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")
            
    def parse_progress(self, line: str) -> tuple[Optional[int], str]:
        """Parse progress from output line.
        
        Args:
            line: Output line
            
        Returns:
            Tuple of (percentage, message) or (None, line)
        """
        # TODO: Implement progress parsing based on RAVE output format
        # Example: Look for patterns like "Step 1000/10000" or "50%"
        return None, line
    
    def stop(self):
        """Stop the running process."""
        self._should_stop = True
        if self.process:
            self.process.terminate()


class RAVEProcess:
    """Helper class for running RAVE CLI commands."""
    
    @staticmethod
    def preprocess(input_path: Path, output_path: Path, 
                  sample_rate: int = 44100, channels: int = 1,
                  num_signal: int = 65536, lazy: bool = False) -> List[str]:
        """Build preprocess command.
        
        Args:
            input_path: Path to input audio files
            output_path: Path to output dataset
            sample_rate: Target sample rate
            channels: Number of audio channels
            num_signal: Number of samples per chunk
            lazy: Use lazy loading
            
        Returns:
            Command as list of strings
        """
        cmd = [
            "rave", "preprocess",
            "--input_path", str(input_path),
            "--output_path", str(output_path),
            "--sampling_rate", str(sample_rate),
            "--channels", str(channels),
            "--num_signal", str(num_signal)
        ]
        
        if lazy:
            cmd.append("--lazy")
            
        return cmd
    
    @staticmethod
    def train(config: str, db_path: Path, name: str,
             overrides: Optional[List[str]] = None) -> List[str]:
        """Build train command.
        
        Args:
            config: Config name (e.g., 'v2')
            db_path: Path to preprocessed dataset
            name: Training run name
            overrides: List of config overrides
            
        Returns:
            Command as list of strings
        """
        cmd = [
            "rave", "train",
            "--config", config,
            "--db_path", str(db_path),
            "--name", name
        ]
        
        if overrides:
            for override in overrides:
                cmd.extend(["--override", override])
                
        return cmd
    
    @staticmethod
    def export(run_path: Path, format: str = "torchscript",
              streaming: bool = False) -> List[str]:
        """Build export command.
        
        Args:
            run_path: Path to training run
            format: Export format (torchscript, onnx)
            streaming: Enable streaming mode
            
        Returns:
            Command as list of strings
        """
        cmd = [
            "rave", "export",
            "--run", str(run_path),
            "--format", format
        ]
        
        if streaming:
            cmd.append("--streaming")
            
        return cmd
