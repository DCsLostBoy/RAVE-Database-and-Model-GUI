"""
Tests for configuration manager.
"""
import pytest
import tempfile
from pathlib import Path
from rave_gui.core.config import ConfigManager


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory with test config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_dir = Path(tmpdir)
        
        # Create test config files
        v2_config = config_dir / "v2.gin"
        v2_config.write_text("""
# Test v2 config
import rave

latent_size = 16
capacity = 64
n_layers = 8
""")
        
        causal_config = config_dir / "causal.gin"
        causal_config.write_text("""
# Causal modifier
causal = True
padding_mode = "causal"
""")
        
        yield config_dir


def test_scan_configs(temp_config_dir):
    """Test scanning for configuration files."""
    manager = ConfigManager(temp_config_dir)
    
    configs = manager.list_configs()
    assert len(configs) == 2
    assert "v2" in configs
    assert "causal" in configs


def test_get_config_path(temp_config_dir):
    """Test retrieving config file path."""
    manager = ConfigManager(temp_config_dir)
    
    path = manager.get_config_path("v2")
    assert path is not None
    assert path.name == "v2.gin"
    assert path.exists()


def test_parse_config(temp_config_dir):
    """Test parsing a configuration file."""
    manager = ConfigManager(temp_config_dir)
    
    config_path = manager.get_config_path("v2")
    assert config_path is not None
    config = manager.parse_config(config_path)
    
    assert "parameters" in config
    assert "latent_size" in config["parameters"]
    assert config["parameters"]["latent_size"] == 16
    assert config["parameters"]["capacity"] == 64


def test_compose_configs(temp_config_dir):
    """Test composing multiple configuration files."""
    manager = ConfigManager(temp_config_dir)
    
    composed = manager.compose_configs(["v2", "causal"])
    
    assert "parameters" in composed
    assert composed["parameters"]["latent_size"] == 16
    assert composed["parameters"]["causal"] is True
    assert composed["config_files"] == ["v2", "causal"]


def test_get_config_categories(temp_config_dir):
    """Test categorizing configurations."""
    manager = ConfigManager(temp_config_dir)
    
    categories = manager.get_config_categories()
    
    assert "base" in categories
    assert "modifiers" in categories
    assert "v2" in categories["base"]
    assert "causal" in categories["modifiers"]


def test_find_rave_configs():
    """Test finding RAVE configs directory."""
    # This test may pass or fail depending on RAVE installation
    config_dir = ConfigManager.find_rave_configs()
    
    # If RAVE is installed, config_dir should be a valid Path
    if config_dir is not None:
        assert isinstance(config_dir, Path)
        assert config_dir.exists()


def test_parse_config_with_comments(temp_config_dir):
    """Test parsing config file with comments."""
    config_file = temp_config_dir / "test_comments.gin"
    config_file.write_text("""
# This is a comment
param1 = 10  # inline comment
# Another comment
param2 = "value"
""")
    
    manager = ConfigManager(temp_config_dir)
    config = manager.parse_config(config_file)
    
    assert config["parameters"]["param1"] == 10
    assert config["parameters"]["param2"] == "value"
