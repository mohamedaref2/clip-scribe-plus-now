
"""
System tray integration for ClipScribe Plus.
"""
import logging
import sys
import platform
from typing import Optional

logger = logging.getLogger(__name__)

# Import platform-specific tray icon implementation
system = platform.system()
try:
    if system == 'Windows':
        from pystray import Icon as TrayIconImpl
        from pystray import Menu, MenuItem
        from PIL import Image
        TRAY_AVAILABLE = True
    elif system == 'Darwin':  # macOS
        from pystray import Icon as TrayIconImpl
        from pystray import Menu, MenuItem
        from PIL import Image
        TRAY_AVAILABLE = True
    else:  # Linux/Unix
        from pystray import Icon as TrayIconImpl
        from pystray import Menu, MenuItem
        from PIL import Image
        TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    logger.warning("pystray not available, tray icon will not be shown")


class TrayIcon:
    """
    System tray icon for the application.
    Provides quick access to application features from the system tray.
    """
    
    def __init__(self, app):
        """
        Initialize the tray icon
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.icon_impl = None
        
        if not TRAY_AVAILABLE:
            logger.warning("System tray icon not available on this platform")
            return
            
        try:
            # Create tray icon
            self._create_tray_icon()
        except Exception as e:
            logger.error(f"Failed to create tray icon: {str(e)}")
            
    def _create_tray_icon(self) -> None:
        """Create the system tray icon"""
        try:
            # Load icon image
            try:
                icon_path = "images/icon.png"
                icon_image = Image.open(icon_path)
            except Exception:
                # Create a simple default icon if the image can't be loaded
                icon_image = Image.new('RGB', (32, 32), color=(0, 120, 220))
                
            # Create menu
            menu = Menu(
                MenuItem("Show", self._on_show),
                MenuItem("Hide", self._on_hide),
                MenuItem("Settings", self._on_settings),
                MenuItem("About", self._on_about),
                MenuItem("Exit", self._on_exit)
            )
            
            # Create icon
            self.icon_impl = TrayIconImpl(
                "ClipScribe Plus",
                icon=icon_image,
                menu=menu
            )
            
            # Start in a separate thread
            self.icon_impl.run_detached()
            logger.info("System tray icon initialized")
            
        except Exception as e:
            logger.error(f"Error creating tray icon: {str(e)}")
            
    def _on_show(self) -> None:
        """Show the main window"""
        self.app.show()
        
    def _on_hide(self) -> None:
        """Hide the main window"""
        self.app.hide()
        
    def _on_settings(self) -> None:
        """Open settings window"""
        self.app.show()  # Show main window first
        # Then open settings dialog (when implemented)
        
    def _on_about(self) -> None:
        """Show about dialog"""
        import tkinter as tk
        
        # Show the main window first
        self.app.show()
        
        # Show about dialog
        tk.messagebox.showinfo(
            "About ClipScribe Plus",
            "ClipScribe Plus - Advanced Clipboard Manager\n"
            "Version 1.0.0\n\n"
            "A powerful clipboard manager with plugin support,\n"
            "custom themes, and advanced features."
        )
        
    def _on_exit(self) -> None:
        """Exit the application"""
        self.app.exit()
        
    def show_notification(self, title: str, message: str) -> None:
        """
        Show a system notification
        
        Args:
            title: Notification title
            message: Notification message
        """
        if self.icon_impl:
            self.icon_impl.notify(title, message)
            
    def remove(self) -> None:
        """Remove the tray icon"""
        if self.icon_impl:
            self.icon_impl.stop()
            self.icon_impl = None
