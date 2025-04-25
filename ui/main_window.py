
"""
Main window of the ClipScribe Plus application.
"""
import logging
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MainWindow:
    """
    Main application window with clipboard list and controls.
    """
    
    def __init__(self, app):
        """
        Initialize the main window
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.root = app.root
        
        # Get settings
        self.settings = app.settings
        
        # Create the window components
        self._create_window()
        self._create_menu()
        self._create_components()
        self._setup_layout()
        self._bind_events()
        
        logger.info("Main window initialized")
        
    def _create_window(self) -> None:
        """Create the main window"""
        # Set window properties
        self.root.title("ClipScribe Plus")
        self.root.geometry("800x600")
        self.root.minsize(400, 300)
        
        # Set window icon if available
        try:
            icon_path = "images/icon.ico" if os.path.exists("images/icon.ico") else "images/icon.png"
            if os.path.exists(icon_path):
                self.icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, self.icon)
        except Exception as e:
            logger.error(f"Error setting window icon: {str(e)}")
            
        # Configure window properties from settings
        always_on_top = self.settings.get("ui", "always_on_top", False)
        opacity = self.settings.get("ui", "opacity", 1.0)
        
        self.root.attributes("-topmost", always_on_top)
        self.root.attributes("-alpha", opacity)
        
    def _create_menu(self) -> None:
        """Create the main menu bar"""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New Window", command=self._new_window)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self._open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.app.on_close)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Clear Clipboard History", command=self._clear_history)
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo", command=self._undo)
        edit_menu.add_command(label="Redo", command=self._redo)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        theme_menu.add_command(label="Light", command=lambda: self._change_theme("light"))
        theme_menu.add_command(label="Dark", command=lambda: self._change_theme("dark"))
        theme_menu.add_command(label="System", command=lambda: self._change_theme("system"))
        theme_menu.add_command(label="High Contrast", command=lambda: self._change_theme("high_contrast"))
        
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        view_menu.add_separator()
        
        # Always on top toggle
        self.always_on_top_var = tk.BooleanVar(value=self.settings.get("ui", "always_on_top", False))
        view_menu.add_checkbutton(label="Always on Top", 
                                  variable=self.always_on_top_var,
                                  command=self._toggle_always_on_top)
                                  
        # Add opacity slider
        view_menu.add_command(label="Opacity...", command=self._show_opacity_dialog)
        
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Plugins menu
        plugins_menu = tk.Menu(self.menu_bar, tearoff=0)
        plugins_menu.add_command(label="Manage Plugins...", command=self._open_plugins)
        self.menu_bar.add_cascade(label="Plugins", menu=plugins_menu)
        
        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self._open_docs)
        help_menu.add_command(label="About", command=self._show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        
    def _create_components(self) -> None:
        """Create UI components"""
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        
        # Toolbar
        self.toolbar = ttk.Frame(self.main_frame)
        
        # New window button
        self.new_window_btn = ttk.Button(
            self.toolbar, text="+", width=3,
            command=self._new_window
        )
        
        # Search box
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            self.toolbar, 
            textvariable=self.search_var,
            width=30
        )
        
        # Clear history button
        self.clear_btn = ttk.Button(
            self.toolbar, 
            text="Clear",
            command=self._clear_history
        )
        
        # Clipboard list frame
        self.list_frame = ttk.Frame(self.main_frame)
        
        # Create a listbox with scrollbar for clipboard items
        self.clip_list = tk.Listbox(
            self.list_frame,
            selectmode=tk.SINGLE,
            activestyle='dotbox',
            font=('Segoe UI', 10),
            height=15
        )
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.list_frame,
            orient=tk.VERTICAL,
            command=self.clip_list.yview
        )
        self.clip_list.config(yscrollcommand=self.scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            anchor=tk.W,
            padding=(5, 2)
        )
        
        # Clipboard content preview frame
        self.preview_frame = ttk.LabelFrame(
            self.main_frame,
            text="Preview",
            padding=(5, 5)
        )
        
        # Text widget for content preview
        self.preview_text = tk.Text(
            self.preview_frame,
            wrap=tk.WORD,
            height=5,
            state=tk.DISABLED
        )
        
    def _setup_layout(self) -> None:
        """Set up the UI layout"""
        # Configure root to expand components
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main frame fills the window
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Toolbar at the top
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.new_window_btn.pack(side=tk.LEFT, padx=5)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Clipboard list in the middle
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=5)
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        
        self.clip_list.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Preview frame
        self.preview_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar at the bottom
        self.status_bar.grid(row=3, column=0, sticky="ew")
        
    def _bind_events(self) -> None:
        """Bind event handlers"""
        # Search as you type
        self.search_var.trace_add("write", lambda *args: self._filter_clipboard_list())
        
        # List selection changed
        self.clip_list.bind("<<ListboxSelect>>", self._on_item_selected)
        
        # Double click to copy and close
        self.clip_list.bind("<Double-Button-1>", self._on_item_double_clicked)
        
        # Right click for context menu
        self.clip_list.bind("<Button-3>", self._show_context_menu)
        
        # Register clipboard change listener
        self.app.clipboard_manager.add_clipboard_change_listener(
            self._on_clipboard_changed
        )
        
    def _on_clipboard_changed(self, clip_item) -> None:
        """
        Handle clipboard change events
        
        Args:
            clip_item: The new clipboard item
        """
        self._update_clipboard_list()
        self.status_var.set("Clipboard updated")
        
    def _update_clipboard_list(self) -> None:
        """Update the displayed clipboard items list"""
        # Clear the list
        self.clip_list.delete(0, tk.END)
        
        # Get filtered items based on search
        search_text = self.search_var.get().lower()
        
        # Add items to the list
        for item in reversed(self.app.clipboard_manager.history):
            # Apply search filter if needed
            if search_text:
                if item.content_type != 'text' or search_text not in item.content.lower():
                    continue
                    
            # Add the item
            if item.content_type == 'text':
                # Get first line or truncate if too long
                display_text = item.content.split('\n')[0]
                if len(display_text) > 50:
                    display_text = display_text[:47] + "..."
                self.clip_list.insert(tk.END, display_text)
            elif item.content_type == 'image':
                self.clip_list.insert(tk.END, f"[Image] {item.timestamp}")
            else:
                self.clip_list.insert(tk.END, f"[{item.content_type}]")
                
        # Select the most recent item if available
        if self.clip_list.size() > 0:
            self.clip_list.selection_set(0)
            self._on_item_selected(None)
            
    def _filter_clipboard_list(self) -> None:
        """Filter the clipboard list based on search text"""
        self._update_clipboard_list()
        
    def _on_item_selected(self, event) -> None:
        """
        Handle item selection in the clipboard list
        
        Args:
            event: The selection event
        """
        selection = self.clip_list.curselection()
        if not selection:
            return
            
        # Get the corresponding clipboard item (in reverse order)
        index = selection[0]
        history_index = len(self.app.clipboard_manager.history) - 1 - index
        
        if 0 <= history_index < len(self.app.clipboard_manager.history):
            item = self.app.clipboard_manager.history[history_index]
            self._update_preview(item)
            
    def _on_item_double_clicked(self, event) -> None:
        """
        Handle double-click on clipboard item
        
        Args:
            event: The mouse event
        """
        selection = self.clip_list.curselection()
        if not selection:
            return
            
        # Get the corresponding clipboard item (in reverse order)
        index = selection[0]
        history_index = len(self.app.clipboard_manager.history) - 1 - index
        
        if 0 <= history_index < len(self.app.clipboard_manager.history):
            item = self.app.clipboard_manager.history[history_index]
            self.app.clipboard_manager.copy_to_clipboard(item)
            self.status_var.set("Copied to clipboard")
            
            # Hide window if configured to do so
            if self.settings.get("general", "hide_after_paste", True):
                self.hide()
                
    def _update_preview(self, item) -> None:
        """
        Update the preview area with the selected item
        
        Args:
            item: The clipboard item to preview
        """
        # Clear current preview
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        # Display content based on type
        if item.content_type == 'text':
            # Text content
            if len(item.content) > 1000:
                # Truncate very long text
                preview = item.content[:1000] + "..."
            else:
                preview = item.content
                
            self.preview_text.insert(tk.END, preview)
            
        elif item.content_type == 'image':
            # For image, just show dimensions
            self.preview_text.insert(tk.END, "[Image]\n")
            # You could display the image here with additional widgets
            
        else:
            # Other content types
            self.preview_text.insert(tk.END, f"[{item.content_type} content]")
            
        self.preview_text.config(state=tk.DISABLED)
        
    def _show_context_menu(self, event) -> None:
        """
        Show context menu on right-click
        
        Args:
            event: The mouse event
        """
        # Get the clicked item
        index = self.clip_list.nearest(event.y)
        if index < 0 or index >= self.clip_list.size():
            return
            
        # Select the clicked item
        self.clip_list.selection_clear(0, tk.END)
        self.clip_list.selection_set(index)
        self.clip_list.activate(index)
        self._on_item_selected(None)
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(
            label="Copy to Clipboard", 
            command=self._copy_selected
        )
        context_menu.add_command(
            label="Delete Item", 
            command=self._delete_selected
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="Move to Top", 
            command=self._move_selected_to_top
        )
        
        # Display the menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
            
    def _copy_selected(self) -> None:
        """Copy the selected item to clipboard"""
        selection = self.clip_list.curselection()
        if not selection:
            return
            
        index = selection[0]
        history_index = len(self.app.clipboard_manager.history) - 1 - index
        
        if 0 <= history_index < len(self.app.clipboard_manager.history):
            item = self.app.clipboard_manager.history[history_index]
            self.app.clipboard_manager.copy_to_clipboard(item)
            self.status_var.set("Copied to clipboard")
            
    def _delete_selected(self) -> None:
        """Delete the selected item"""
        selection = self.clip_list.curselection()
        if not selection:
            return
            
        index = selection[0]
        history_index = len(self.app.clipboard_manager.history) - 1 - index
        
        if 0 <= history_index < len(self.app.clipboard_manager.history):
            del self.app.clipboard_manager.history[history_index]
            self._update_clipboard_list()
            self.status_var.set("Item deleted")
            
    def _move_selected_to_top(self) -> None:
        """Move the selected item to the top of the list"""
        selection = self.clip_list.curselection()
        if not selection:
            return
            
        index = selection[0]
        history_index = len(self.app.clipboard_manager.history) - 1 - index
        
        if 0 <= history_index < len(self.app.clipboard_manager.history):
            # Get the item
            item = self.app.clipboard_manager.history[history_index]
            
            # Remove from current position
            del self.app.clipboard_manager.history[history_index]
            
            # Add to end (which is the top in the display)
            self.app.clipboard_manager.history.append(item)
            
            # Update the UI
            self._update_clipboard_list()
            self.status_var.set("Item moved to top")
            
    def _clear_history(self) -> None:
        """Clear clipboard history"""
        if len(self.app.clipboard_manager.history) == 0:
            return
            
        self.app.clipboard_manager.history.clear()
        self._update_clipboard_list()
        self.status_var.set("Clipboard history cleared")
        
    def _new_window(self) -> None:
        """Create and show a new clipboard manager window"""
        # In a real implementation, this would create a new process
        # For now, just show a message
        self.status_var.set("New window feature not implemented")
        
    def _open_settings(self) -> None:
        """Open settings dialog"""
        # This would open a settings dialog - placeholder for now
        self.status_var.set("Settings dialog not implemented")
        
    def _open_plugins(self) -> None:
        """Open plugins manager"""
        # This would open a plugin manager - placeholder for now
        self.status_var.set("Plugin manager not implemented")
        
    def _open_docs(self) -> None:
        """Open documentation"""
        # This would open documentation - placeholder for now
        self.status_var.set("Documentation not implemented")
        
    def _show_about(self) -> None:
        """Show about dialog"""
        # Show a simple about message box
        tk.messagebox.showinfo(
            "About ClipScribe Plus",
            "ClipScribe Plus - Advanced Clipboard Manager\n"
            "Version 1.0.0\n\n"
            "A powerful clipboard manager with plugin support,\n"
            "custom themes, and advanced features."
        )
        
    def _undo(self) -> None:
        """Undo last clipboard operation"""
        item = self.app.clipboard_manager.undo()
        if item:
            self._update_clipboard_list()
            self.status_var.set("Undone last operation")
        else:
            self.status_var.set("Nothing to undo")
            
    def _redo(self) -> None:
        """Redo previously undone clipboard operation"""
        item = self.app.clipboard_manager.redo()
        if item:
            self._update_clipboard_list()
            self.status_var.set("Redone last operation")
        else:
            self.status_var.set("Nothing to redo")
            
    def _change_theme(self, theme_id: str) -> None:
        """
        Change the application theme
        
        Args:
            theme_id: The ID of the theme to apply
        """
        success = self.app.theme_manager.apply_theme(theme_id)
        if success:
            # Update settings
            self.app.settings.set("ui", "theme", theme_id)
            self.app.settings.save()
            self.status_var.set(f"Theme changed to {theme_id}")
        else:
            self.status_var.set(f"Failed to change theme to {theme_id}")
            
    def _toggle_always_on_top(self) -> None:
        """Toggle always-on-top window state"""
        always_on_top = self.always_on_top_var.get()
        self.root.attributes("-topmost", always_on_top)
        self.app.settings.set("ui", "always_on_top", always_on_top)
        self.app.settings.save()
        
        self.status_var.set(f"Always on top: {'On' if always_on_top else 'Off'}")
        
    def _show_opacity_dialog(self) -> None:
        """Show dialog to adjust window opacity"""
        # Create a simple dialog with a slider
        dialog = tk.Toplevel(self.root)
        dialog.title("Window Opacity")
        dialog.geometry("300x100")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Current opacity
        current_opacity = self.app.settings.get("ui", "opacity", 1.0)
        
        # Label
        ttk.Label(dialog, text="Window Opacity:").pack(pady=5)
        
        # Opacity var
        opacity_var = tk.DoubleVar(value=current_opacity)
        
        # Function to update opacity live
        def update_opacity(*args):
            value = opacity_var.get()
            self.root.attributes("-alpha", value)
            
        # Slider
        slider = ttk.Scale(
            dialog,
            from_=0.2, to=1.0,
            orient=tk.HORIZONTAL,
            variable=opacity_var,
            command=update_opacity
        )
        slider.pack(fill=tk.X, padx=20, pady=5)
        
        # Button frame
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # OK button
        def ok_clicked():
            value = opacity_var.get()
            self.app.settings.set("ui", "opacity", value)
            self.app.settings.save()
            dialog.destroy()
            
        ttk.Button(btn_frame, text="OK", command=ok_clicked).pack(side=tk.RIGHT, padx=5)
        
        # Cancel button
        def cancel_clicked():
            self.root.attributes("-alpha", current_opacity)
            dialog.destroy()
            
        ttk.Button(btn_frame, text="Cancel", command=cancel_clicked).pack(side=tk.RIGHT, padx=5)
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
    def show(self) -> None:
        """Show the main window"""
        self.root.deiconify()
        self.root.lift()
        self._update_clipboard_list()
        
    def hide(self) -> None:
        """Hide the main window"""
        self.root.withdraw()
        
    def toggle_visibility(self) -> None:
        """Toggle window visibility"""
        if self.root.state() == 'withdrawn':
            self.show()
        else:
            self.hide()
            
    def destroy(self) -> None:
        """Clean up resources before destruction"""
        # Nothing special to clean up for now
        pass
