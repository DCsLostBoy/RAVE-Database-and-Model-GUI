"""
SQLite database interface for RAVE GUI.
"""
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class Database:
    """SQLite database interface for storing project metadata."""
    
    def __init__(self, db_path: Path):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.initialize_schema()
        
    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            
    def initialize_schema(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Datasets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
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
        """)
        
        # Experiments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                dataset_id INTEGER,
                config TEXT,
                status TEXT DEFAULT 'not_started',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                metrics TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (dataset_id) REFERENCES datasets(id)
            )
        """)
        
        # Models table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id INTEGER,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                checkpoint_step INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experiment_id) REFERENCES experiments(id)
            )
        """)
        
        # Exports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                format TEXT NOT NULL,
                path TEXT NOT NULL,
                streaming BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models(id)
            )
        """)
        
        self.conn.commit()
        
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Cursor object
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one row from query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Row dictionary or None
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows from query.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of row dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
