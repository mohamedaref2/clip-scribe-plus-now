
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
        "last_used_to_top": True,
        "allow_window_maximize": False,  # New option to control window maximization
        "auto_collapse": {
            "enabled": True,
            "position": "right",  # top, bottom, right, left
            "delay_seconds": 1.5
        }
    },
    "ui": {
        "theme": "dark",  # Default to dark theme
        "language": "en",
        "opacity": 0.98,  # Slightly transparent for Mica effect
        "always_on_top": False,
        "show_timestamps": True,
        "font_size": 12,
        "enable_auto_collapse": True,
        "modern_menu": True,  # New option for modern menu styling
        "show_menu_bar": False  # Hide traditional menu bar by default
    },
    "hotkeys": {
        "toggle_visibility": "ctrl+shift+c",
        "paste_last_item": "ctrl+shift+v",
        "clear_history": "ctrl+shift+x",
        "new_window": "ctrl+shift+n"  # New hotkey for creating a new window
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
        "items": [],
        "sticky_items": []
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

    # Notes management methods
    def add_note(self, note_data: Dict) -> bool:
        """
        Add a new note
        
        Args:
            note_data: Note data dictionary with content, timestamp, etc.
            
        Returns:
            bool: True if added successfully
        """
        if "notes" not in self.settings:
            self.settings["notes"] = {"items": [], "sticky_items": []}
            
        self.settings["notes"]["items"].append(note_data)
        return self.save()
        
    def get_notes(self) -> list:
        """
        Get all notes
        
        Returns:
            List of notes
        """
        return self.settings.get("notes", {}).get("items", [])
        
    def get_sticky_notes(self) -> list:
        """
        Get sticky notes
        
        Returns:
            List of sticky notes
        """
        return self.settings.get("notes", {}).get("sticky_items", [])
        
    def toggle_note_sticky(self, note_id: str) -> bool:
        """
        Toggle whether a note is sticky
        
        Args:
            note_id: ID of the note
            
        Returns:
            bool: New sticky state
        """
        found = False
        note_data = None
        
        # Look for note in regular items
        for note in self.settings["notes"]["items"]:
            if note.get("id") == note_id:
                found = True
                note_data = note
                self.settings["notes"]["items"].remove(note)
                self.settings["notes"]["sticky_items"].append(note)
                break
                
        # If not found in regular items, check sticky items
        if not found:
            for note in self.settings["notes"]["sticky_items"]:
                if note.get("id") == note_id:
                    found = True
                    note_data = note
                    self.settings["notes"]["sticky_items"].remove(note)
                    self.settings["notes"]["items"].append(note)
                    break
                    
        if found and note_data:
            self.save()
            return note_id in [n.get("id") for n in self.settings["notes"]["sticky_items"]]
            
        return False
        
    def move_note(self, note_id: str, direction: str) -> bool:
        """
        Move a note up, down, top or bottom
        
        Args:
            note_id: ID of the note
            direction: Direction to move (up, down, top, bottom)
            
        Returns:
            bool: True if moved successfully
        """
        # Determine which list contains the note
        container = None
        note_index = -1
        note_data = None
        
        # Check regular items
        for i, note in enumerate(self.settings["notes"]["items"]):
            if note.get("id") == note_id:
                container = self.settings["notes"]["items"]
                note_index = i
                note_data = note
                break
                
        # Check sticky items if not found
        if note_index == -1:
            for i, note in enumerate(self.settings["notes"]["sticky_items"]):
                if note.get("id") == note_id:
                    container = self.settings["notes"]["sticky_items"]
                    note_index = i
                    note_data = note
                    break
                    
        # If note was found, move it
        if container and note_index >= 0 and note_data:
            container.pop(note_index)
            
            if direction == "up" and note_index > 0:
                container.insert(note_index - 1, note_data)
            elif direction == "down" and note_index < len(container):
                container.insert(note_index + 1, note_data)
            elif direction == "top":
                container.insert(0, note_data)
            elif direction == "bottom":
                container.append(note_data)
            else:
                # Invalid direction, put it back
                container.insert(note_index, note_data)
                return False
                
            self.save()
            return True
            
        return False
        
    def update_note_used(self, note_id: str) -> bool:
        """
        Mark a note as recently used and move to top if setting enabled
        
        Args:
            note_id: ID of the note
            
        Returns:
            bool: True if updated successfully
        """
        # Only proceed if last_used_to_top is enabled
        if not self.get("general", "last_used_to_top", True):
            return False
            
        # Only move notes in the regular items list, not sticky
        note_index = -1
        note_data = None
        
        for i, note in enumerate(self.settings["notes"]["items"]):
            if note.get("id") == note_id:
                note_index = i
                note_data = note
                break
                
        if note_index >= 0 and note_data:
            # Update the last used timestamp
            note_data["last_used"] = {
                "timestamp": import_time().time(),
                "date": import_time().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Move to top
            self.settings["notes"]["items"].pop(note_index)
            self.settings["notes"]["items"].insert(0, note_data)
            
            self.save()
            return True
            
        return False

# Helper for time functions
def import_time():
    """Import time module on demand to avoid circular imports"""
    import time
    return time
