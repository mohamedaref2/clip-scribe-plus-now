
"""
Theme manager for the application UI.
Provides functionality to load, apply, and switch UI themes.
"""
import json
import logging
import os
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Default themes
DEFAULT_THEMES = {
    "light": {
        "name": "Light",
        "description": "Default light theme",
        "colors": {
            "background": "#f0f0f0",
            "foreground": "#333333",
            "accent": "#007bff",
            "secondary": "#6c757d",
            "success": "#28a745",
            "danger": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8",
            "border": "#dee2e6",
            "highlight": "#e9ecef"
        },
        "fonts": {
            "main": ("Segoe UI", 10),
            "title": ("Segoe UI", 12, "bold"),
            "monospace": ("Consolas", 10)
        }
    },
    "dark": {
        "name": "Dark",
        "description": "Default dark theme",
        "colors": {
            "background": "#212529",
            "foreground": "#f8f9fa",
            "accent": "#007bff",
            "secondary": "#adb5bd",
            "success": "#28a745",
            "danger": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8",
            "border": "#495057",
            "highlight": "#343a40"
        },
        "fonts": {
            "main": ("Segoe UI", 10),
            "title": ("Segoe UI", 12, "bold"),
            "monospace": ("Consolas", 10)
        }
    },
    "high_contrast": {
        "name": "High Contrast",
        "description": "High contrast accessibility theme",
        "colors": {
            "background": "#000000",
            "foreground": "#ffffff",
            "accent": "#ffff00",
            "secondary": "#ffffff",
            "success": "#00ff00",
            "danger": "#ff0000",
            "warning": "#ffff00",
            "info": "#00ffff",
            "border": "#ffffff",
            "highlight": "#444444"
        },
        "fonts": {
            "main": ("Segoe UI", 12),
            "title": ("Segoe UI", 14, "bold"),
            "monospace": ("Consolas", 12)
        }
    }
}


class ThemeManager:
    """
    Manages UI themes for the application.
    """
    
    def __init__(self, themes_dir: str = "themes"):
        """
        Initialize theme manager
        
        Args:
            themes_dir: Directory containing theme files
        """
        self.themes_dir = themes_dir
        self.themes = DEFAULT_THEMES.copy()
        self.current_theme = "light"  # Default theme
        self.ttk_style = None
        
        # Ensure themes directory exists
        os.makedirs(themes_dir, exist_ok=True)
        
        # Load custom themes
        self._load_custom_themes()
        
    def _load_custom_themes(self) -> None:
        """Load custom themes from theme directory"""
        try:
            theme_files = [f for f in os.listdir(self.themes_dir) 
                          if f.endswith('.json')]
                          
            for file in theme_files:
                try:
                    with open(os.path.join(self.themes_dir, file), 'r') as f:
                        theme_data = json.load(f)
                        
                    theme_id = os.path.splitext(file)[0]
                    
                    # Validate theme structure
                    if self._validate_theme(theme_data):
                        self.themes[theme_id] = theme_data
                        logger.info(f"Loaded custom theme: {theme_data.get('name', theme_id)}")
                except Exception as e:
                    logger.error(f"Error loading theme file {file}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error loading custom themes: {str(e)}")
            
    def _validate_theme(self, theme: Dict) -> bool:
        """
        Validate a theme's structure
        
        Args:
            theme: Theme data to validate
            
        Returns:
            bool: True if theme is valid, False otherwise
        """
        # Basic validation
        if not isinstance(theme, dict):
            return False
            
        required_keys = ["name", "colors", "fonts"]
        for key in required_keys:
            if key not in theme:
                logger.warning(f"Theme missing required key: {key}")
                return False
                
        return True
        
    def get_theme_list(self) -> List[Dict]:
        """
        Get list of available themes
        
        Returns:
            List of dictionaries with theme info
        """
        return [
            {"id": theme_id, "name": theme_data.get("name", theme_id)}
            for theme_id, theme_data in self.themes.items()
        ]
        
    def get_system_theme(self) -> str:
        """
        Detect system theme preference
        
        Returns:
            Theme ID based on system preference
        """
        try:
            # This is a simple implementation - in practice, you'd use
            # platform-specific methods to detect dark mode
            import darkdetect
            is_dark = darkdetect.isDark()
            return "dark" if is_dark else "light"
        except ImportError:
            logger.warning("darkdetect not available, defaulting to light theme")
            return "light"
            
    def initialize_ttk_style(self, root: tk.Tk) -> None:
        """
        Initialize TTK style for theming
        
        Args:
            root: Root Tk instance
        """
        self.ttk_style = ttk.Style(root)
        self.apply_theme(self.current_theme)
        
    def apply_theme(self, theme_id: str) -> bool:
        """
        Apply a theme to the application
        
        Args:
            theme_id: ID of the theme to apply
            
        Returns:
            bool: True if theme applied successfully, False otherwise
        """
        # Handle "system" theme
        if theme_id == "system":
            theme_id = self.get_system_theme()
            
        # Check if theme exists
        if theme_id not in self.themes:
            logger.error(f"Theme not found: {theme_id}")
            return False
            
        # Get the theme data
        theme = self.themes[theme_id]
        
        # Store current theme
        self.current_theme = theme_id
        
        # If TTK style is not initialized, we're done
        if not self.ttk_style:
            logger.warning("TTK style not initialized, theme will be applied later")
            return True
            
        try:
            # Configure ttk styles
            self._configure_ttk_styles(theme)
            
            # Configure colors for regular tk widgets
            self._configure_tk_colors(theme)
            
            logger.info(f"Theme applied: {theme.get('name', theme_id)}")
            return True
        except Exception as e:
            logger.error(f"Error applying theme {theme_id}: {str(e)}")
            return False
            
    def _configure_ttk_styles(self, theme: Dict) -> None:
        """
        Configure TTK styles based on theme
        
        Args:
            theme: Theme data dictionary
        """
        colors = theme.get("colors", {})
        fonts = theme.get("fonts", {})
        
        # Configure the base style
        self.ttk_style.configure(
            ".",
            background=colors.get("background"),
            foreground=colors.get("foreground"),
            font=fonts.get("main"),
            bordercolor=colors.get("border"),
            darkcolor=colors.get("highlight"),
            lightcolor=colors.get("background"),
            troughcolor=colors.get("highlight"),
            arrowcolor=colors.get("foreground"),
            insertcolor=colors.get("foreground")
        )
        
        # Configure specific widget styles
        self.ttk_style.configure(
            "TButton",
            background=colors.get("accent"),
            foreground=colors.get("background")
        )
        
        self.ttk_style.map(
            "TButton",
            background=[("active", colors.get("secondary"))],
            foreground=[("active", colors.get("background"))]
        )
        
        self.ttk_style.configure(
            "TLabel",
            background=colors.get("background"),
            foreground=colors.get("foreground")
        )
        
        self.ttk_style.configure(
            "TFrame",
            background=colors.get("background")
        )
        
        # Add more widget styles as needed
        
    def _configure_tk_colors(self, theme: Dict) -> None:
        """
        Configure colors for regular tk widgets
        
        Args:
            theme: Theme data dictionary
        """
        # This would apply to all windows/widgets created after this point
        # For existing widgets, they would need to be updated individually
        colors = theme.get("colors", {})
        tk.ACTIVE_BACKGROUND = colors.get("accent")
        tk.ACTIVE_FOREGROUND = colors.get("background")
        tk.BACKGROUND = colors.get("background")
        tk.FOREGROUND = colors.get("foreground")
        
    def create_theme(self, theme_id: str, theme_data: Dict) -> bool:
        """
        Create a new theme
        
        Args:
            theme_id: ID for the new theme
            theme_data: Theme data dictionary
            
        Returns:
            bool: True if created successfully, False otherwise
        """
        if not self._validate_theme(theme_data):
            logger.error("Invalid theme data")
            return False
            
        # Add to themes dictionary
        self.themes[theme_id] = theme_data
        
        # Save to file
        try:
            with open(os.path.join(self.themes_dir, f"{theme_id}.json"), 'w') as f:
                json.dump(theme_data, f, indent=4)
                
            logger.info(f"Created theme: {theme_data.get('name', theme_id)}")
            return True
        except Exception as e:
            logger.error(f"Error saving theme {theme_id}: {str(e)}")
            return False
            
    def delete_theme(self, theme_id: str) -> bool:
        """
        Delete a theme
        
        Args:
            theme_id: ID of the theme to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        # Don't allow deleting built-in themes
        if theme_id in DEFAULT_THEMES:
            logger.error(f"Cannot delete built-in theme: {theme_id}")
            return False
            
        # Remove from themes dictionary
        if theme_id in self.themes:
            del self.themes[theme_id]
            
        # Delete file if it exists
        theme_file = os.path.join(self.themes_dir, f"{theme_id}.json")
        if os.path.exists(theme_file):
            try:
                os.remove(theme_file)
                logger.info(f"Deleted theme: {theme_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting theme file: {str(e)}")
                return False
        else:
            logger.warning(f"Theme file not found: {theme_id}")
            return True  # Still successful since theme is gone
