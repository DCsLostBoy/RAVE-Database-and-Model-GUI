"""
Dataset operations backend.
"""
from pathlib import Path
from typing import Optional, List, Dict
import json


class DatasetManager:
    """Manages dataset preprocessing and storage."""
    
    def __init__(self, db_connection):
        """Initialize the dataset manager.
        
        Args:
            db_connection: Database connection object
        """
        self.db = db_connection
        
    def create_dataset(self, config: Dict) -> int:
        """Create a new dataset.
        
        Args:
            config: Dataset configuration dictionary containing:
                - name: Dataset name
                - path: Output path for preprocessed dataset
                - input_path: Path to input audio files
                - project_id: Optional project ID
                - num_samples: Number of samples (default: None)
                - channels: Number of audio channels
                - sample_rate: Sampling rate
                
        Returns:
            Dataset ID
        """
        # Validate required fields
        if not config.get('name'):
            raise ValueError("Dataset name is required")
        if not config.get('path'):
            raise ValueError("Dataset path is required")
            
        # Insert into database
        cursor = self.db.execute(
            """INSERT INTO datasets 
               (project_id, name, path, num_samples, channels, sample_rate)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                config.get('project_id'),
                config['name'],
                str(config['path']),
                config.get('num_samples'),
                config.get('channels', 1),
                config.get('sample_rate', 44100)
            )
        )
        
        return cursor.lastrowid
    
    def get_dataset(self, dataset_id: int) -> Optional[Dict]:
        """Get dataset by ID.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Dataset dictionary or None
        """
        return self.db.fetch_one(
            "SELECT * FROM datasets WHERE id = ?",
            (dataset_id,)
        )
    
    def list_datasets(self, project_id: Optional[int] = None) -> List[Dict]:
        """List all datasets, optionally filtered by project.
        
        Args:
            project_id: Optional project ID to filter by
            
        Returns:
            List of dataset dictionaries
        """
        if project_id is not None:
            return self.db.fetch_all(
                "SELECT * FROM datasets WHERE project_id = ? ORDER BY created_at DESC",
                (project_id,)
            )
        else:
            return self.db.fetch_all(
                "SELECT * FROM datasets ORDER BY created_at DESC"
            )
    
    def delete_dataset(self, dataset_id: int) -> bool:
        """Delete a dataset.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            True if successful
        """
        try:
            self.db.execute(
                "DELETE FROM datasets WHERE id = ?",
                (dataset_id,)
            )
            return True
        except Exception:
            return False
    
    def get_dataset_stats(self, dataset_id: int) -> Dict:
        """Get statistics for a dataset.
        
        Args:
            dataset_id: Dataset ID
            
        Returns:
            Statistics dictionary with keys:
                - total_samples: Total number of samples
                - duration_seconds: Total duration in seconds
                - channels: Number of channels
                - sample_rate: Sampling rate
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            return {}
            
        # Calculate duration based on samples and sample rate
        num_samples = dataset.get('num_samples', 0)
        sample_rate = dataset.get('sample_rate', 44100)
        
        duration_seconds = num_samples / sample_rate if sample_rate > 0 and num_samples else 0
        
        return {
            'total_samples': num_samples,
            'duration_seconds': duration_seconds,
            'channels': dataset.get('channels', 1),
            'sample_rate': sample_rate
        }
