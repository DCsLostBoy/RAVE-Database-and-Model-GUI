"""
Configuration file parsing and management.
"""
from pathlib import Path
from typing import List, Dict, Optional
import json
import sys
import re
import ast


class ConfigManager:
    """Manager for RAVE Gin configuration files."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the config manager.
        
        Args:
            config_dir: Directory containing Gin config files
        """
        self.config_dir = config_dir or self.find_rave_configs()
        self.configs = self.scan_configs()
        
    @staticmethod
    def find_rave_configs() -> Optional[Path]:
        """Find the RAVE configs directory.
        
        Returns:
            Path to configs directory or None
        """
        # Try to find rave package in Python path
        try:
            import rave
            rave_path = Path(rave.__file__).parent
            config_dir = rave_path / "configs"
            if config_dir.exists():
                return config_dir
        except ImportError:
            pass
        
        # Check relative to this file (development setup)
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent  # Go up from rave_gui/core/config.py
        rave_configs = project_root / "rave" / "configs"
        if rave_configs.exists():
            return rave_configs
        
        # Check common installation paths
        possible_paths = [
            Path(sys.prefix) / "lib" / "python*" / "site-packages" / "rave" / "configs",
            Path.home() / ".local" / "lib" / "python*" / "site-packages" / "rave" / "configs",
        ]
        
        for path_pattern in possible_paths:
            matches = list(path_pattern.parent.parent.glob("python*/site-packages/rave/configs"))
            if matches:
                return matches[0]
        
        return None
    
    def scan_configs(self) -> Dict[str, Path]:
        """Scan for available configuration files.
        
        Returns:
            Dictionary mapping config names to paths
        """
        configs = {}
        
        if not self.config_dir or not self.config_dir.exists():
            return configs
        
        # Scan for .gin files
        for config_file in self.config_dir.glob("**/*.gin"):
            name = config_file.stem
            configs[name] = config_file
            
        return configs
    
    def get_config_path(self, config_name: str) -> Optional[Path]:
        """Get path to a configuration file.
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Path to config file or None
        """
        return self.configs.get(config_name)
    
    def list_configs(self) -> List[str]:
        """List available configuration names.
        
        Returns:
            List of configuration names
        """
        return list(self.configs.keys())
    
    def parse_config(self, config_path: Path) -> Dict:
        """Parse a Gin configuration file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Dictionary of configuration parameters
        """
        config = {
            "imports": [],
            "parameters": {},
            "includes": []
        }
        
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse include statements
                if line.startswith('include'):
                    match = re.search(r'include\s+[\'"](.+)[\'"]', line)
                    if match:
                        config["includes"].append(match.group(1))
                
                # Parse import statements
                elif line.startswith('import'):
                    match = re.search(r'import\s+(.+)', line)
                    if match:
                        config["imports"].append(match.group(1).strip())
                
                # Parse parameter assignments
                elif '=' in line:
                    # Split on first = only
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        
                        # Try to evaluate simple Python literals
                        try:
                            # Remove comments from value
                            if '#' in value:
                                value = value.split('#')[0].strip()
                            
                            # Try to parse as Python literal
                            value = ast.literal_eval(value)
                        except (ValueError, SyntaxError):
                            # Keep as string if not a valid literal
                            pass
                        
                        config["parameters"][key] = value
                        
        return config
    
    def compose_configs(self, config_names: List[str]) -> Dict:
        """Compose multiple configuration files.
        
        Args:
            config_names: List of config names to compose
            
        Returns:
            Composed configuration dictionary
        """
        composed = {
            "imports": [],
            "parameters": {},
            "includes": [],
            "config_files": []
        }
        
        for name in config_names:
            config_path = self.get_config_path(name)
            if config_path:
                config = self.parse_config(config_path)
                
                # Merge imports and includes
                composed["imports"].extend(config.get("imports", []))
                composed["includes"].extend(config.get("includes", []))
                
                # Merge parameters (later configs override earlier ones)
                composed["parameters"].update(config.get("parameters", {}))
                
                # Track which files were used
                composed["config_files"].append(name)
                
        # Remove duplicates from imports and includes
        composed["imports"] = list(dict.fromkeys(composed["imports"]))
        composed["includes"] = list(dict.fromkeys(composed["includes"]))
                
        return composed
    
    def get_config_categories(self) -> Dict[str, List[str]]:
        """Categorize configurations into base models and modifiers.
        
        Returns:
            Dictionary with 'base' and 'modifiers' categories
        """
        base_configs = []
        modifiers = []
        
        for name in self.list_configs():
            # Base models typically have version numbers or are in root
            if any(version in name for version in ['v1', 'v2', 'v3']):
                base_configs.append(name)
            else:
                modifiers.append(name)
        
        return {
            "base": sorted(base_configs),
            "modifiers": sorted(modifiers)
        }
    
    def save_config(self, config: Dict, output_path: Path):
        """Save a configuration to JSON.
        
        Args:
            config: Configuration dictionary
            output_path: Output file path
        """
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
