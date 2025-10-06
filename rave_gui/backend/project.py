"""
Project management backend.
"""
from pathlib import Path
from typing import Optional, List, Dict


class ProjectManager:
    """Manages RAVE GUI projects."""
    
    def __init__(self, db_connection):
        """Initialize the project manager.
        
        Args:
            db_connection: Database connection object
        """
        self.db = db_connection
        
    def create_project(self, name: str, path: str) -> int:
        """Create a new project.
        
        Args:
            name: Project name
            path: Project directory path
            
        Returns:
            Project ID
            
        Raises:
            ValueError: If project name already exists
        """
        # Check if project name already exists
        existing = self.db.fetch_one(
            "SELECT id FROM projects WHERE name = ?",
            (name,)
        )
        if existing:
            raise ValueError(f"Project '{name}' already exists")
        
        # Create project directory if it doesn't exist
        project_path = Path(path)
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Insert project into database
        cursor = self.db.execute(
            "INSERT INTO projects (name, path) VALUES (?, ?)",
            (name, str(project_path))
        )
        
        return cursor.lastrowid
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project dictionary or None
        """
        return self.db.fetch_one(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,)
        )
    
    def get_project_by_name(self, name: str) -> Optional[Dict]:
        """Get project by name.
        
        Args:
            name: Project name
            
        Returns:
            Project dictionary or None
        """
        return self.db.fetch_one(
            "SELECT * FROM projects WHERE name = ?",
            (name,)
        )
    
    def list_projects(self) -> List[Dict]:
        """List all projects.
        
        Returns:
            List of project dictionaries
        """
        return self.db.fetch_all(
            "SELECT * FROM projects ORDER BY created_at DESC"
        )
    
    def delete_project(self, project_id: int) -> bool:
        """Delete a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if successful
        """
        self.db.execute(
            "DELETE FROM projects WHERE id = ?",
            (project_id,)
        )
        return True
    
    def update_project(self, project_id: int, name: Optional[str] = None, 
                      path: Optional[str] = None) -> bool:
        """Update a project.
        
        Args:
            project_id: Project ID
            name: New project name (optional)
            path: New project path (optional)
            
        Returns:
            True if successful
        """
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if path is not None:
            updates.append("path = ?")
            params.append(str(path))
        
        if not updates:
            return False
        
        params.append(project_id)
        query = f"UPDATE projects SET {', '.join(updates)} WHERE id = ?"
        
        self.db.execute(query, tuple(params))
        return True
