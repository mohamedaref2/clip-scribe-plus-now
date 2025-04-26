
"""
Context menu implementation for ClipScribe Plus.
"""
import logging
import tkinter as tk
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class ContextMenu:
    """
    Right-click context menu implementation.
    """
    
    def __init__(self, parent: tk.Widget, theme_manager=None):
        """
        Initialize context menu
        
        Args:
            parent: Parent widget
            theme_manager: ThemeManager instance for styling
        """
        self.parent = parent
        self.theme_manager = theme_manager
        self.menu = tk.Menu(parent, tearoff=0)
        self._apply_theme()
        
    def _apply_theme(self) -> None:
        """Apply current theme to menu"""
        if not self.theme_manager:
            return
            
        try:
            theme_id = self.theme_manager.current_theme
            if theme_id in self.theme_manager.themes:
                theme = self.theme_manager.themes[theme_id]
                colors = theme.get("colors", {})
                
                # Configure menu appearance
                self.menu.config(
                    background=colors.get("highlight", "#2C2C2C"),
                    foreground=colors.get("foreground", "#FFFFFF"),
                    activebackground=colors.get("accent", "#9b87f5"),
                    activeforeground=colors.get("background", "#1A1F2C"),
                    borderwidth=1,
                    relief="solid"
                )
        except Exception as e:
            logger.error(f"Error applying theme to context menu: {str(e)}")
            
    def add_command(self, label: str, command: Callable[[], None], **kwargs) -> None:
        """
        Add a command to the context menu
        
        Args:
            label: Menu item label
            command: Function to call when clicked
            **kwargs: Additional arguments for menu.add_command
        """
        self.menu.add_command(label=label, command=command, **kwargs)
        
    def add_separator(self) -> None:
        """Add a separator to the context menu"""
        self.menu.add_separator()
        
    def add_submenu(self, label: str) -> 'ContextMenu':
        """
        Add a submenu to the context menu
        
        Args:
            label: Submenu label
            
        Returns:
            ContextMenu: New submenu instance
        """
        submenu = ContextMenu(self.parent, self.theme_manager)
        self.menu.add_cascade(label=label, menu=submenu.menu)
        return submenu
        
    def add_checkbutton(self, label: str, variable: tk.BooleanVar, **kwargs) -> None:
        """
        Add a checkbutton to the context menu
        
        Args:
            label: Menu item label
            variable: BooleanVar to store state
            **kwargs: Additional arguments for menu.add_checkbutton
        """
        self.menu.add_checkbutton(label=label, variable=variable, **kwargs)
        
    def add_radiobutton(self, label: str, variable: tk.StringVar, value: str, **kwargs) -> None:
        """
        Add a radiobutton to the context menu
        
        Args:
            label: Menu item label
            variable: StringVar to store selected value
            value: Value for this option
            **kwargs: Additional arguments for menu.add_radiobutton
        """
        self.menu.add_radiobutton(label=label, variable=variable, value=value, **kwargs)
        
    def popup(self, event) -> None:
        """
        Show the context menu at the event position
        
        Args:
            event: Event with x_root and y_root coordinates
        """
        try:
            # Apply theme before showing (in case theme changed)
            self._apply_theme()
            
            # Show menu at click position
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            # Make sure to release the grab
            self.menu.grab_release()
            
    def clear(self) -> None:
        """Remove all items from the context menu"""
        self.menu.delete(0, 'end')


class ClipboardItemContextMenu(ContextMenu):
    """
    Context menu specialized for clipboard items.
    """
    
    def __init__(self, parent: tk.Widget, app, item_id: str, theme_manager=None):
        """
        Initialize clipboard item context menu
        
        Args:
            parent: Parent widget
            app: ClipScribeApp instance
            item_id: Clipboard item ID
            theme_manager: ThemeManager instance
        """
        super().__init__(parent, theme_manager)
        self.app = app
        self.item_id = item_id
        self._build_menu()
        
    def _build_menu(self) -> None:
        """Build the context menu items"""
        self.add_command("Copy", self._copy_item)
        self.add_command("Paste", self._paste_item)
        self.add_separator()
        self.add_command("Edit", self._edit_item)
        self.add_command("Delete", self._delete_item)
        self.add_separator()
        
        # Add plugin actions submenu if plugins are available
        if hasattr(self.app, 'plugin_manager'):
            plugins_submenu = self.add_submenu("Plugin Actions")
            plugin_actions = self.app.plugin_manager.get_item_actions(self.item_id)
            
            if plugin_actions:
                for action in plugin_actions:
                    plugins_submenu.add_command(
                        action.get("label", "Action"),
                        lambda a=action: self._execute_plugin_action(a)
                    )
            else:
                plugins_submenu.add_command("No actions available", lambda: None, state="disabled")
                
    def _copy_item(self) -> None:
        """Copy the clipboard item to the clipboard"""
        try:
            item = self.app.clipboard_manager.get_item_by_id(self.item_id)
            if item:
                self.app.clipboard_manager.copy_to_clipboard(item)
        except Exception as e:
            logger.error(f"Error copying item: {str(e)}")
            
    def _paste_item(self) -> None:
        """Copy item to clipboard and simulate paste"""
        self._copy_item()
        self.app.paste_last_item()
        
    def _edit_item(self) -> None:
        """Open editor for the clipboard item"""
        try:
            # This would call the edit dialog implementation
            if hasattr(self.app.main_window, 'edit_clipboard_item'):
                self.app.main_window.edit_clipboard_item(self.item_id)
        except Exception as e:
            logger.error(f"Error editing item: {str(e)}")
            
    def _delete_item(self) -> None:
        """Delete the clipboard item"""
        try:
            self.app.clipboard_manager.delete_item(self.item_id)
            # Refresh the UI if needed
            if hasattr(self.app.main_window, 'refresh_history'):
                self.app.main_window.refresh_history()
        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            
    def _execute_plugin_action(self, action: Dict) -> None:
        """
        Execute a plugin action on the clipboard item
        
        Args:
            action: Plugin action dictionary
        """
        try:
            callback = action.get("callback")
            if callable(callback):
                item = self.app.clipboard_manager.get_item_by_id(self.item_id)
                if item:
                    callback(item)
        except Exception as e:
            logger.error(f"Error executing plugin action: {str(e)}")


class NoteContextMenu(ContextMenu):
    """
    Context menu specialized for notes.
    """
    
    def __init__(self, parent: tk.Widget, app, note_id: str, theme_manager=None):
        """
        Initialize note context menu
        
        Args:
            parent: Parent widget
            app: ClipScribeApp instance
            note_id: Note ID
            theme_manager: ThemeManager instance
        """
        super().__init__(parent, theme_manager)
        self.app = app
        self.note_id = note_id
        self._build_menu()
        
    def _build_menu(self) -> None:
        """Build the context menu items"""
        self.add_command("Copy to Clipboard", self._copy_note)
        self.add_separator()
        self.add_command("Edit", self._edit_note)
        self.add_command("Delete", self._delete_note)
        self.add_separator()
        
        # Note position submenu
        position_submenu = self.add_submenu("Position")
        position_submenu.add_command("Move Up", lambda: self._move_note("up"))
        position_submenu.add_command("Move Down", lambda: self._move_note("down"))
        position_submenu.add_command("Move to Top", lambda: self._move_note("top"))
        position_submenu.add_command("Move to Bottom", lambda: self._move_note("bottom"))
        
        # Pin/Unpin toggle
        is_sticky = self._is_note_sticky()
        pin_label = "Unpin Note" if is_sticky else "Pin to Top"
        self.add_command(pin_label, self._toggle_sticky)
        
    def _copy_note(self) -> None:
        """Copy the note content to clipboard"""
        try:
            notes = self.app.settings.get_notes() + self.app.settings.get_sticky_notes()
            for note in notes:
                if note.get("id") == self.note_id:
                    content = note.get("content", "")
                    self.app.clipboard_manager.set_clipboard_text(content)
                    break
        except Exception as e:
            logger.error(f"Error copying note: {str(e)}")
            
    def _edit_note(self) -> None:
        """Open editor for the note"""
        try:
            # This would call the note editor implementation
            if hasattr(self.app.main_window, 'edit_note'):
                self.app.main_window.edit_note(self.note_id)
        except Exception as e:
            logger.error(f"Error editing note: {str(e)}")
            
    def _delete_note(self) -> None:
        """Delete the note"""
        try:
            # This would call the note deletion implementation
            if hasattr(self.app.main_window, 'delete_note'):
                self.app.main_window.delete_note(self.note_id)
        except Exception as e:
            logger.error(f"Error deleting note: {str(e)}")
            
    def _move_note(self, direction: str) -> None:
        """
        Move the note in the specified direction
        
        Args:
            direction: Direction to move (up, down, top, bottom)
        """
        try:
            self.app.settings.move_note(self.note_id, direction)
            # Refresh notes display
            if hasattr(self.app.main_window, 'refresh_notes'):
                self.app.main_window.refresh_notes()
        except Exception as e:
            logger.error(f"Error moving note: {str(e)}")
            
    def _toggle_sticky(self) -> None:
        """Toggle the note's sticky status"""
        try:
            self.app.settings.toggle_note_sticky(self.note_id)
            # Refresh notes display
            if hasattr(self.app.main_window, 'refresh_notes'):
                self.app.main_window.refresh_notes()
        except Exception as e:
            logger.error(f"Error toggling note sticky state: {str(e)}")
            
    def _is_note_sticky(self) -> bool:
        """Check if the note is sticky"""
        sticky_notes = self.app.settings.get_sticky_notes()
        return any(note.get("id") == self.note_id for note in sticky_notes)
