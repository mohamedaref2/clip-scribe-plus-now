
"""
Settings management module for storing and retrieving application settings.
"""
import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "general": {
        "max_history_items": 100,
        "clipboard_poll_interval": 0.5,
        "start_minimized": False,
        "start_with_system": False,
        "confirm_delete": True,
        "hide_after_paste": True,
        "minimize_to_tray_on_close": True,
        "last_used_to_top": True
    },
    "ui": {
        "theme": "dark",  # Changed to dark by default
        "language": "en",
        "opacity": 0.98,  # Slightly transparent for Mica effect
        "always_on_top": False,
        "show_timestamps": True,
        "font_size": 12,
        "enable_auto_collapse": True
    },
    "hotkeys": {
        "toggle_visibility": "ctrl+shift+c",
        "paste_last_item": "ctrl+shift+v",
        "clear_history": "ctrl+shift+x"
    },
    "plugins": {
        "enabled": []
    },
    "security": {
        "encrypt_sensitive": False,
        "encrypt_key": "",
        "auto_clear_passwords": True
    },
    "notes": {
        "items": []
    }
}


class Settings:
    """
    Manages application settings with JSON file storage and in-memory cache.
    """
    
    def __init__(self, settings_file: str = "config/settings.json"):
        """
        Initialize settings manager
        
        Args:
            settings_file: Path to the settings JSON file
        """
        self.settings_file = settings_file
        self.settings = {}
        self.load()
        
    def load(self) -> None:
        """Load settings from file or create with defaults if not exists"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            # Try to load from file
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    
                # Merge with defaults to ensure all needed settings exist
                self._merge_settings(DEFAULT_SETTINGS, loaded)
                logger.info("Settings loaded from file")
            else:
                # Use defaults
                self.settings = DEFAULT_SETTINGS.copy()
                self.save()  # Create the file
                logger.info("Created new settings file with defaults")
                
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            logger.info("Using default settings")
            self.settings = DEFAULT_SETTINGS.copy()
            
    def save(self) -> bool:
        """
        Save current settings to file
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            # Write settings to file
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
                
            logger.info("Settings saved to file")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            return False
            
    def _merge_settings(self, default: Dict, loaded: Dict) -> None:
        """
        Recursively merge loaded settings with defaults
        
        Args:
            default: Default settings dictionary
            loaded: Loaded settings dictionary
        """
        self.settings = default.copy()
        
        for key, value in loaded.items():
            if key in self.settings and isinstance(self.settings[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                for subkey, subvalue in value.items():
                    if subkey in self.settings[key]:
                        self.settings[key][subkey] = subvalue
            else:
                self.settings[key] = value
                
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a setting value
        
        Args:
            section: Settings section name
            key: Setting key name
            default: Default value if not found
            
        Returns:
            Setting value or default if not found
        """
        try:
            return self.settings.get(section, {}).get(key, default)
        except Exception:
            return default
            
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a setting value
        
        Args:
            section: Settings section name
            key: Setting key name
            value: Value to set
        """
        if section not in self.settings:
            self.settings[section] = {}
            
        self.settings[section][key] = value
        
    def get_section(self, section: str) -> Dict:
        """
        Get an entire settings section
        
        Args:
            section: Section name
            
        Returns:
            Dictionary of settings in the section or empty dict if not found
        """
        return self.settings.get(section, {})
        
    def set_section(self, section: str, values: Dict) -> None:
        """
        Set an entire settings section
        
        Args:
            section: Section name
            values: Dictionary of settings to set
        """
        self.settings[section] = values
        
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.settings = DEFAULT_SETTINGS.copy()
        self.save()
        logger.info("Settings reset to defaults")
        
    def reset_section(self, section: str) -> None:
        """
        Reset a specific section to defaults
        
        Args:
            section: Section name to reset
        """
        if section in DEFAULT_SETTINGS:
            self.settings[section] = DEFAULT_SETTINGS[section].copy()
            self.save()
            logger.info(f"Section {section} reset to defaults")

