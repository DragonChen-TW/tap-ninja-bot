"""
Configuration manager for Tap Ninja Helper.
Handles loading, saving, and accessing user settings.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    "capture_interval": 5,  # seconds
    "parent_area": {
        "x1": 0,
        "y1": 0,
        "x2": 800,
        "y2": 600
    },
    "capture_area": {
        "x1": 0,
        "y1": 0,
        "x2": 300,
        "y2": 300
    },
    "use_two_step_capture": True,  # Whether to use the two-step capture process
    "ocr_areas": []  # Will contain dictionaries with x1, y1, x2, y2, and label
}

class Config:
    """Configuration manager class"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. If None, uses default.
        """
        if config_path is None:
            # Get the directory of this file
            base_dir = Path(__file__).resolve().parent.parent
            self.config_path = os.path.join(base_dir, "data", "settings.json")
        else:
            self.config_path = config_path
            
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create with defaults if it doesn't exist.
        
        Returns:
            Dict containing the configuration
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, use defaults
                return DEFAULT_CONFIG.copy()
        else:
            # Create new config with defaults and save it
            self.save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    
    def save(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save. If None, saves current config.
        """
        if config is not None:
            self.config = config
            
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key to get
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and save.
        
        Args:
            key: Configuration key to set
            value: Value to set
        """
        self.config[key] = value
        self.save()
        
    def get_tesseract_path(self) -> str:
        """Get the path to Tesseract OCR executable."""
        return self.get("tesseract_path", DEFAULT_CONFIG["tesseract_path"])
