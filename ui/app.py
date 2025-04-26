
"""
Main application class for ClipScribe Plus.
"""
import logging
import os
import threading
import tkinter as tk
from tkinter import messagebox
import sys
import uuid
from typing import Dict, List, Optional

from core.clipboard_manager import ClipboardManager
from core.hotkeys import HotkeyManager
from core.plugin_manager import PluginManager
from data.settings import Settings
from ui.theme_manager import ThemeManager
from ui.main_window import MainWindow
from ui.tray_icon import TrayIcon

logger = logging.getLogger(__name__)

class ClipScribeApp:
    """
    Main application class that coordinates all components.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the application
        
        Args:
            root: Root Tk instance
        """
        self.root = root
        self.root.withdraw()  # Hide main window initially
        
        logger.info("Initializing ClipScribe Plus application")
        
        # Set root window title
        self.root.title("ClipScribe Plus")
        
        # Set up shutdown handlers
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Initialize components
        self.settings = Settings()
        self.theme_manager = ThemeManager()
        self.clipboard_manager = ClipboardManager(
            max_history=self.settings.get("general", "max_history_items", 100)
        )
        self.hotkey_manager = HotkeyManager()
        self.plugin_manager = PluginManager(self)
        
        # Register clipboard change listener for plugins
        self.clipboard_manager.add_clipboard_change_listener(
            self.plugin_manager.notify_clipboard_change
        )
        
        # Initialize theme - always light
        self.theme_manager.initialize_ttk_style(self.root)
        
        # Create main window
        self.main_window = MainWindow(self)
        
        # Create system tray icon
        self.tray_icon = TrayIcon(self)
        
        # Windows list for multi-window support
        self.windows = [self.main_window]
        
        # Start services
        self._start_services()
        
        # Load plugins
        threading.Thread(target=self._load_plugins, daemon=True).start()
        
        # Set up global hotkeys
        self._setup_hotkeys()
        
        # Disable maximize button
        self._disable_maximize()
        
        # Determine initial visibility
        start_minimized = self.settings.get("general", "start_minimized", False)
        if not start_minimized:
            self.show()
        else:
            self.hide()
            
        logger.info("ClipScribe Plus initialization complete")
    
    def _disable_maximize(self) -> None:
        """Disable maximize button on the window"""
        try:
            # This is Windows-specific
            import ctypes
            GWL_STYLE = -16
            WS_MAXIMIZEBOX = 0x00010000
            
            hwnd = self.root.winfo_id()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            style = style & ~WS_MAXIMIZEBOX
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
            logger.info("Maximize button disabled")
        except Exception as e:
            logger.error(f"Failed to disable maximize button: {str(e)}")
        
    def _start_services(self) -> None:
        """Start all background services"""
        # Start clipboard monitoring
        poll_interval = self.settings.get("general", "clipboard_poll_interval", 0.5)
        self.clipboard_manager.start_monitoring(interval=poll_interval)
        
        # Start hotkey listener
        self.hotkey_manager.start()
        
    def _setup_hotkeys(self) -> None:
        """Set up global hotkeys from settings"""
        # Toggle visibility hotkey
        toggle_key = self.settings.get("hotkeys", "toggle_visibility", "ctrl+shift+c")
        self.hotkey_manager.register_hotkey(
            toggle_key,
            lambda: self.toggle_visibility(),
            "Toggle ClipScribe Plus visibility"
        )
        
        # Paste last item hotkey
        paste_key = self.settings.get("hotkeys", "paste_last_item", "ctrl+shift+v")
        self.hotkey_manager.register_hotkey(
            paste_key,
            lambda: self.paste_last_item(),
            "Paste last clipboard item"
        )
        
        # New window hotkey
        new_window_key = self.settings.get("hotkeys", "new_window", "ctrl+shift+n")
        self.hotkey_manager.register_hotkey(
            new_window_key,
            lambda: self.create_new_window(),
            "Create new ClipScribe window"
        )
        
    def _load_plugins(self) -> None:
        """Load and initialize plugins"""
        try:
            plugins = self.plugin_manager.load_all_plugins()
            
            # Enable plugins that should be enabled
            enabled_plugins = self.settings.get("plugins", "enabled", [])
            for plugin_name in enabled_plugins:
                if plugin_name in plugins:
                    self.plugin_manager.enable_plugin(plugin_name)
                    
            logger.info(f"Loaded {len(plugins)} plugins, enabled {len(enabled_plugins)}")
        except Exception as e:
            logger.error(f"Error loading plugins: {str(e)}")
    
    def add_note(self, content: str) -> bool:
        """
        Add a new note to settings
        
        Args:
            content: Note content
            
        Returns:
            bool: True if added successfully
        """
        try:
            import time
            
            note_id = str(uuid.uuid4())
            timestamp = time.time()
            date_str = time.strftime("%Y-%m-%d %H:%M:%S")
            
            note_data = {
                "id": note_id,
                "content": content,
                "created": {
                    "timestamp": timestamp,
                    "date": date_str
                },
                "last_used": {
                    "timestamp": timestamp,
                    "date": date_str
                }
            }
            
            success = self.settings.add_note(note_data)
            
            if success:
                logger.info(f"Added new note: {note_id}")
                # Refresh the main window to show the new note
                self.main_window.refresh_notes()
                return True
            else:
                logger.error("Failed to add note")
                return False
                
        except Exception as e:
            logger.error(f"Error adding note: {str(e)}")
            return False
            
    def update_note(self, note_id: str, content: str) -> bool:
        """
        Update an existing note
        
        Args:
            note_id: ID of the note to update
            content: New content
            
        Returns:
            bool: True if updated successfully
        """
        try:
            # Get all notes from settings
            all_notes = self.settings.get_notes()
            sticky_notes = self.settings.get_sticky_notes()
            
            # Look for the note in regular notes
            for note in all_notes:
                if note.get("id") == note_id:
                    note["content"] = content
                    self.settings.save()
                    logger.info(f"Updated note: {note_id}")
                    self.main_window.refresh_notes()
                    return True
                    
            # Look for the note in sticky notes
            for note in sticky_notes:
                if note.get("id") == note_id:
                    note["content"] = content
                    self.settings.save()
                    logger.info(f"Updated sticky note: {note_id}")
                    self.main_window.refresh_notes()
                    return True
                    
            logger.warning(f"Note not found: {note_id}")
            return False
                
        except Exception as e:
            logger.error(f"Error updating note: {str(e)}")
            return False
    
    def show(self) -> None:
        """Show the main application window"""
        self.main_window.show()
        
    def hide(self) -> None:
        """Hide the main application window"""
        self.main_window.hide()
        
    def toggle_visibility(self) -> None:
        """Toggle the visibility of the main window"""
        self.main_window.toggle_visibility()
        
    def paste_last_item(self) -> None:
        """Paste the most recent clipboard item"""
        if self.clipboard_manager.history:
            self.clipboard_manager.copy_to_clipboard(self.clipboard_manager.history[-1])
            # Simulate Ctrl+V
            # This would require platform-specific code, example:
            try:
                from pynput.keyboard import Key, Controller
                keyboard = Controller()
                keyboard.press(Key.ctrl)
                keyboard.press('v')
                keyboard.release('v')
                keyboard.release(Key.ctrl)
                
                # Hide window after paste if enabled
                if self.settings.get("general", "hide_after_paste", True):
                    self.hide()
            except Exception as e:
                logger.error(f"Error simulating paste: {str(e)}")
    
    def create_new_window(self) -> None:
        """Create a new ClipScribe window"""
        try:
            # Create new Toplevel window
            new_window = tk.Toplevel(self.root)
            new_window.withdraw()  # Hide until fully configured
            
            # Create new MainWindow instance
            window = MainWindow(self, new_window)
            self.windows.append(window)
            
            # Disable maximize on new window
            self._disable_maximize_on_window(new_window)
            
            # Show the new window
            window.show()
            
            logger.info("Created new ClipScribe window")
        except Exception as e:
            logger.error(f"Error creating new window: {str(e)}")
    
    def _disable_maximize_on_window(self, window) -> None:
        """Disable maximize button on a window"""
        try:
            # This is Windows-specific
            import ctypes
            GWL_STYLE = -16
            WS_MAXIMIZEBOX = 0x00010000
            
            hwnd = window.winfo_id()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            style = style & ~WS_MAXIMIZEBOX
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
        except Exception as e:
            logger.error(f"Failed to disable maximize button on child window: {str(e)}")
                
    def on_close(self) -> None:
        """Handle application close event"""
        try:
            # Check if we should minimize to tray instead
            if self.settings.get("general", "minimize_to_tray_on_close", True):
                self.hide()
                return
                
            # Confirm before exit
            if messagebox.askokcancel("Quit", "Do you want to quit ClipScribe Plus?"):
                self.exit()
        except Exception as e:
            logger.error(f"Error during close: {str(e)}")
            self.exit()
            
    def exit(self) -> None:
        """Exit the application"""
        logger.info("Shutting down ClipScribe Plus")
        
        # Clean shutdown of components
        try:
            # Save settings
            self.settings.save()
            
            # Stop clipboard monitoring
            self.clipboard_manager.stop_monitoring()
            
            # Stop hotkey listener
            self.hotkey_manager.stop()
            
            # Shut down plugins
            self.plugin_manager.shutdown()
            
            # Remove tray icon
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.remove()
                
            # Close all windows
            for window in self.windows:
                if window:
                    window.destroy()
            
            # Destroy root
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
            
        finally:
            # Force exit if needed
            logger.info("ClipScribe Plus has shut down")
            sys.exit(0)
