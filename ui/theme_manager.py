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

# Default theme - Light only
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
        },
        "styles": {
            "Modern.TFrame": {"background": "#f0f0f0"},
            "Modern.TButton": {"background": "#007bff", "foreground": "#FFFFFF"},
            "Modern.TLabel": {"background": "#f0f0f0", "foreground": "#333333"},
            "Modern.Title.TLabel": {"background": "#f0f0f0", "foreground": "#333333", "font": ("Segoe UI", 12, "bold")},
            "Modern.TEntry": {"fieldbackground": "#FFFFFF", "foreground": "#333333"},
            "Modern.TSpinbox": {"fieldbackground": "#FFFFFF", "foreground": "#333333"},
            "Modern.TLabelframe": {"background": "#f0f0f0", "foreground": "#333333"},
            "Status.TLabel": {"background": "#e9ecef", "foreground": "#555555"},
            "Toolbar.TFrame": {"background": "#e9ecef"},
            "Modern.TCheckbutton": {"background": "#f0f0f0", "foreground": "#333333"},
            "Modern.TRadiobutton": {"background": "#f0f0f0", "foreground": "#333333"},
            "Modern.Horizontal.TScale": {"background": "#f0f0f0"},
            "Modern.Vertical.TScrollbar": {"background": "#f0f0f0", "troughcolor": "#e9ecef", "arrowcolor": "#333333"},
            "Indicator.TFrame": {"background": "#007bff"},
            "Modern.MenuButton.TButton": {"background": "#f0f0f0", "foreground": "#333333"},
            "Context.TMenu": {"background": "#FFFFFF", "foreground": "#333333"}
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
        self.current_theme = "light"  # Default to light theme only
        self.ttk_style = None
        self.root = None
        
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
            logger.warning("darkdetect not available, defaulting to dark theme")
            return "dark"  # Change default to dark theme
            
    def initialize_ttk_style(self, root: tk.Tk) -> None:
        """
        Initialize TTK style for theming
        
        Args:
            root: Root Tk instance
        """
        self.root = root
        self.ttk_style = ttk.Style(root)
        
        # Define custom styles
        self._define_custom_styles()
        
        # Apply theme - always light
        self.apply_theme("light")
        
    def _define_custom_styles(self) -> None:
        """Define custom ttk styles used by the application"""
        if not self.ttk_style:
            return
            
        # Create modern button style
        self.ttk_style.configure(
            "Modern.TButton",
            padding=(10, 5),
            relief="flat",
            borderwidth=0
        )
        
        # Create menu button style
        self.ttk_style.configure(
            "Modern.MenuButton.TButton", 
            padding=(10, 5),
            relief="flat",
            borderwidth=0
        )
        
        # Create title label style
        self.ttk_style.configure(
            "Modern.Title.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        
        # Create status label style
        self.ttk_style.configure(
            "Status.TLabel",
            padding=(5, 2),
            relief="flat"
        )
        
        # Define modern scale style
        self.ttk_style.configure(
            "Modern.Horizontal.TScale",
            sliderthickness=20,
            sliderlength=15
        )
        
        # Create modern entry style
        self.ttk_style.configure(
            "Modern.TEntry",
            padding=(5, 5),
            borderwidth=1
        )
        
        # Create modern spinbox style
        self.ttk_style.configure(
            "Modern.TSpinbox",
            padding=(5, 5),
            borderwidth=1
        )
        
        # Create modern labelframe style
        self.ttk_style.configure(
            "Modern.TLabelframe",
            padding=10,
            relief="flat",
            borderwidth=1
        )
        self.ttk_style.configure(
            "Modern.TLabelframe.Label",
            font=("Segoe UI", 10, "bold")
        )
        
        # Create indicator frame style
        self.ttk_style.configure(
            "Indicator.TFrame",
            relief="flat",
            borderwidth=0
        )
        
    def apply_theme(self, theme_id: str) -> bool:
        """
        Apply a theme to the application
        
        Args:
            theme_id: ID of the theme to apply
            
        Returns:
            bool: True if theme applied successfully, False otherwise
        """
        # Always use light theme
        theme_id = "light"
            
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
            
            # Apply Mica effect if on Windows 11
            self._apply_mica_effect()
            
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
        styles = theme.get("styles", {})
        
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
            foreground=colors.get("foreground")
        )
        
        self.ttk_style.map(
            "TButton",
            background=[("active", colors.get("secondary"))],
            foreground=[("active", colors.get("foreground"))]
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
        
        # Apply custom styles from theme if available
        if styles:
            for style_name, style_options in styles.items():
                self.ttk_style.configure(style_name, **style_options)
                
                # Apply style maps if needed
                if style_name == "Modern.TButton":
                    self.ttk_style.map(
                        style_name,
                        background=[
                            ("active", colors.get("secondary")), 
                            ("pressed", self._lighten_color(colors.get("secondary"), -0.1))
                        ]
                    )
                elif style_name == "Modern.MenuButton.TButton":
                    self.ttk_style.map(
                        style_name,
                        background=[
                            ("active", colors.get("highlight")), 
                            ("pressed", self._lighten_color(colors.get("highlight"), 0.1))
                        ]
                    )
                
    def _configure_tk_colors(self, theme: Dict) -> None:
        """
        Configure colors for regular tk widgets
        
        Args:
            theme: Theme data dictionary
        """
        if not self.root:
            return
            
        colors = theme.get("colors", {})
        
        # Update option database for new widgets
        self.root.option_add("*Background", colors.get("background"))
        self.root.option_add("*Foreground", colors.get("foreground"))
        self.root.option_add("*selectBackground", colors.get("accent"))
        self.root.option_add("*selectForeground", colors.get("background"))
        self.root.option_add("*Menu.Background", colors.get("highlight"))
        self.root.option_add("*Menu.Foreground", colors.get("foreground"))
        self.root.option_add("*Menu.selectBackground", colors.get("accent"))
        self.root.option_add("*Menu.selectForeground", colors.get("background"))
        
    def _apply_mica_effect(self) -> None:
        """Apply Mica effect on Windows 11"""
        if not self.root:
            return
            
        try:
            import ctypes
            import platform
            
            # Check if running on Windows 11
            if platform.system() == "Windows" and int(platform.version().split('.')[0]) >= 10:
                # Get window handle
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                
                # Constants for Windows 11 Mica effect
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                DWMWA_MICA_EFFECT = 1029
                
                # Apply light mode for title bar (required for Mica)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 
                    DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(ctypes.c_int(0)), 
                    ctypes.sizeof(ctypes.c_int)
                )
                
                # Apply Mica effect
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd,
                    DWMWA_MICA_EFFECT,
                    ctypes.byref(ctypes.c_int(1)),
                    ctypes.sizeof(ctypes.c_int)
                )
                
                logger.info("Applied Mica effect to window")
        except Exception as e:
            logger.warning(f"Could not apply Mica effect: {str(e)}")
    
    def _lighten_color(self, color_hex: str, amount: float = 0.2) -> str:
        """
        Lighten or darken a hex color
        
        Args:
            color_hex: Hex color string (e.g. '#RRGGBB')
            amount: Amount to lighten (positive) or darken (negative)
            
        Returns:
            Modified hex color string
        """
        if not color_hex or not color_hex.startswith('#'):
            return color_hex
            
        try:
            # Convert hex to RGB
            r = int(color_hex[1:3], 16)
            g = int(color_hex[3:5], 16)
            b = int(color_hex[5:7], 16)
            
            # Adjust values
            r = max(0, min(255, int(r + (255 * amount))))
            g = max(0, min(255, int(g + (255 * amount))))
            b = max(0, min(255, int(b + (255 * amount))))
            
            # Convert back to hex
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            return color_hex
            
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
