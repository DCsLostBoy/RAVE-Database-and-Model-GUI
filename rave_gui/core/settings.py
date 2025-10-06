"""
Application settings management.
"""
import json
from pathlib import Path
from typing import Any, Optional


class SettingsManager:
    """Manager for application settings."""
    
    DEFAULT_SETTINGS = {
        "theme": "dark",
        "default_dataset_path": str(Path.home() / "Documents" / "RAVE" / "datasets"),
        "default_models_path": str(Path.home() / "Documents" / "RAVE" / "models"),
        "default_exports_path": str(Path.home() / "Documents" / "RAVE" / "exports"),
        "last_project_id": None,
        "window_geometry": None,
        "recent_projects": [],
    }
    
    def __init__(self, settings_path: Optional[Path] = None):
        """Initialize settings manager.
        
        Args:
            settings_path: Path to settings file
        """
        if settings_path is None:
            config_dir = Path.home() / ".rave_gui"
            config_dir.mkdir(parents=True, exist_ok=True)
            settings_path = config_dir / "settings.json"
        
        self.settings_path = settings_path
        self.settings = self.load_settings()
    
    def load_settings(self) -> dict:
        """Load settings from file.
        
        Returns:
            Settings dictionary
        """
        if not self.settings_path.exists():
            return self.DEFAULT_SETTINGS.copy()
        
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                
            # Merge with defaults to ensure all keys exist
            merged = self.DEFAULT_SETTINGS.copy()
            merged.update(settings)
            return merged
            
        except (json.JSONDecodeError, IOError):
            # If settings file is corrupted, return defaults
            return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Failed to save settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key doesn't exist
            
        Returns:
            Setting value
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value
        self.save_settings()
    
    def get_theme(self) -> str:
        """Get current theme.
        
        Returns:
            Theme name ('dark' or 'light')
        """
        return self.settings.get("theme", "dark")
    
    def set_theme(self, theme: str):
        """Set theme.
        
        Args:
            theme: Theme name ('dark' or 'light')
        """
        if theme in ["dark", "light"]:
            self.set("theme", theme)
    
    def add_recent_project(self, project_id: int, max_recent: int = 10):
        """Add project to recent projects list.
        
        Args:
            project_id: Project ID
            max_recent: Maximum number of recent projects to keep
        """
        recent = self.settings.get("recent_projects", [])
        
        # Remove if already in list
        if project_id in recent:
            recent.remove(project_id)
        
        # Add to front
        recent.insert(0, project_id)
        
        # Trim to max size
        recent = recent[:max_recent]
        
        self.set("recent_projects", recent)
    
    def get_recent_projects(self) -> list:
        """Get list of recent project IDs.
        
        Returns:
            List of project IDs
        """
        return self.settings.get("recent_projects", [])
