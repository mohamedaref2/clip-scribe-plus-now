
"""
Main application window for ClipScribe Plus.
"""
import logging
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import uuid
from typing import Callable, Dict, List, Optional, Any, Union

logger = logging.getLogger(__name__)

class MainWindow:
    """
    Main application window that shows clipboard history and manages user interactions.
    """
    
    def __init__(self, app, parent=None):
        """
        Initialize the main window.
        
        Args:
            app: Parent application instance
            parent: Parent window (tk.Tk or tk.Toplevel)
        """
        self.app = app
        self.parent = parent or app.root
        self.visible = False
        self.collapsible = True
        self.collapsed = False
        self.collapse_timer = None
        
        # Auto-collapse settings
        self.auto_collapse_enabled = app.settings.get("ui", "enable_auto_collapse", True)
        self.auto_collapse_position = app.settings.get("general", "auto_collapse", {}).get("position", "right")
        self.auto_collapse_delay = app.settings.get("general", "auto_collapse", {}).get("delay_seconds", 1.5) * 1000
        
        # Create window if not already provided
        if isinstance(parent, tk.Tk) or isinstance(parent, tk.Toplevel):
            self.window = parent
        else:
            self.window = tk.Toplevel(self.parent)
            self.window.withdraw()
        
        # Configure the window
        self._configure_window()
        
        # Initialize content
        self._init_ui()
        
        # Bind events
        self._bind_events()
        
        logger.info("Main window initialized")
        
    def _configure_window(self) -> None:
        """Configure window properties"""
        # Set window title
        self.window.title("ClipScribe Plus")
        
        # Set minimum size
        self.window.minsize(300, 300)
        
        # Set initial size and position
        self.window.geometry("400x500+100+100")
        
        # Set window icon
        try:
            import os
            icon_path = os.path.join("images", "icon.ico")
            if os.path.exists(icon_path):
                self.window.iconbitmap(icon_path)
            else:
                logger.warning(f"Window icon not found: {icon_path}")
        except Exception as e:
            logger.error(f"Error setting window icon: {str(e)}")
            
        # Set window to always be on top if configured
        if self.app.settings.get("ui", "always_on_top", False):
            self.window.attributes('-topmost', True)
            
        # Set window opacity
        opacity = self.app.settings.get("ui", "opacity", 0.98)
        try:
            self.window.attributes("-alpha", opacity)
        except Exception:
            logger.warning("Window opacity not supported on this platform")
            
        # Configure close behavior
        self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
    def _init_ui(self) -> None:
        """Initialize user interface"""
        # Create main container
        self.main_frame = ttk.Frame(self.window, style="Modern.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self._create_header()
        
        # Create content area
        self._create_content_area()
        
        # Create status bar
        self._create_status_bar()
        
        # Initial content refresh
        self.refresh_content()
        
    def _create_header(self) -> None:
        """Create header with toolbar and title"""
        # Create header frame
        self.header_frame = ttk.Frame(self.main_frame, style="Toolbar.TFrame")
        self.header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create modern toolbar with big icon buttons
        self.toolbar = ttk.Frame(self.header_frame, style="Toolbar.TFrame")
        self.toolbar.pack(fill=tk.X, padx=0, pady=0)
        
        # Create toolbar buttons
        self._create_toolbar_buttons()
        
    def _create_toolbar_buttons(self) -> None:
        """Create modern toolbar buttons"""
        button_size = 40
        button_padding = 8
        
        # Left-aligned buttons
        self.btn_new = self._create_tool_button(
            self.toolbar, "New Note", self.on_new_note,
            "➕", button_size, 0
        )
        
        self.btn_settings = self._create_tool_button(
            self.toolbar, "Settings", self.on_settings,
            "⚙", button_size, 1
        )
        
        self.btn_plugins = self._create_tool_button(
            self.toolbar, "Plugins", self.on_plugins,
            "🔌", button_size, 2
        )
        
        # Right-aligned buttons
        self.btn_minimize = self._create_tool_button(
            self.toolbar, "Minimize", self.hide,
            "—", button_size, -1, True
        )
        
        self.btn_close = self._create_tool_button(
            self.toolbar, "Close", self.on_window_close,
            "✕", button_size, -2, True
        )
        
    def _create_tool_button(self, parent, tooltip, command, text, size, position, right_align=False) -> ttk.Button:
        """Create a toolbar button"""
        button_frame = ttk.Frame(parent)
        
        if right_align:
            button_frame.pack(side=tk.RIGHT, padx=2)
        else:
            button_frame.pack(side=tk.LEFT, padx=2)
            
        button = ttk.Button(
            button_frame, 
            text=text,
            width=3,
            style="Modern.TButton",
            command=command
        )
        button.pack(padx=2, pady=2)
        
        # Add tooltip using a simple hover event
        def show_tooltip(event, tip=tooltip):
            x, y, _, _ = button.bbox("insert")
            x += button.winfo_rootx() + 25
            y += button.winfo_rooty() + 25
            
            # Create a toplevel window
            self.tooltip = tk.Toplevel(button)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(self.tooltip, text=tip, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            
        def hide_tooltip(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()
                
        button.bind("<Enter>", show_tooltip)
        button.bind("<Leave>", hide_tooltip)
        
        return button
        
    def _create_content_area(self) -> None:
        """Create the main content area"""
        # Create content frame with tabs
        self.content_frame = ttk.Frame(self.main_frame, style="Modern.TFrame")
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook with tabs
        self.notebook = ttk.Notebook(self.content_frame)
        
        # Create clipboard history tab
        self.history_frame = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.notebook.add(self.history_frame, text="History")
        
        # Create notes tab
        self.notes_frame = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.notebook.add(self.notes_frame, text="Notes")
        
        # Pack the notebook
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create history content
        self._create_history_content()
        
        # Create notes content
        self._create_notes_content()
        
    def _create_history_content(self) -> None:
        """Create clipboard history content"""
        # Create frame for the history list
        self.history_list_frame = ttk.Frame(self.history_frame, style="Modern.TFrame")
        self.history_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create listbox with scrollbar
        self.history_scrollbar = ttk.Scrollbar(self.history_list_frame)
        self.history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(
            self.history_list_frame,
            bg=self.app.theme_manager.themes["light"]["colors"]["background"],
            fg=self.app.theme_manager.themes["light"]["colors"]["foreground"],
            selectbackground=self.app.theme_manager.themes["light"]["colors"]["accent"],
            selectforeground="#FFFFFF",
            font=self.app.theme_manager.themes["light"]["fonts"]["main"],
            bd=0,
            highlightthickness=0,
            yscrollcommand=self.history_scrollbar.set
        )
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        self.history_scrollbar.config(command=self.history_listbox.yview)
        
        # Bind events
        self.history_listbox.bind("<Double-1>", self.on_history_item_double_click)
        self.history_listbox.bind("<Button-3>", self.on_history_item_right_click)
        
    def _create_notes_content(self) -> None:
        """Create notes content"""
        # Create scrollable frame for the notes
        self.notes_frame_outer = ttk.Frame(self.notes_frame, style="Modern.TFrame")
        self.notes_frame_outer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.notes_scrollbar = ttk.Scrollbar(self.notes_frame_outer)
        self.notes_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.notes_canvas = tk.Canvas(
            self.notes_frame_outer,
            bg=self.app.theme_manager.themes["light"]["colors"]["background"],
            bd=0,
            highlightthickness=0,
            yscrollcommand=self.notes_scrollbar.set
        )
        self.notes_canvas.pack(fill=tk.BOTH, expand=True)
        self.notes_scrollbar.config(command=self.notes_canvas.yview)
        
        # Create an inner frame for the notes
        self.notes_inner_frame = ttk.Frame(self.notes_canvas, style="Modern.TFrame")
        self.notes_canvas_window = self.notes_canvas.create_window(
            (0, 0), 
            window=self.notes_inner_frame, 
            anchor="nw",
            tags="self.notes_inner_frame"
        )
        
        # Configure canvas scrolling
        self.notes_inner_frame.bind("<Configure>", self._on_notes_frame_configure)
        self.notes_canvas.bind("<Configure>", self._on_notes_canvas_configure)
        
        # Bind mouse wheel scrolling
        self.notes_canvas.bind_all("<MouseWheel>", self._on_notes_mousewheel)
        
        # Add a note button
        self.add_note_frame = ttk.Frame(self.notes_frame_outer, style="Modern.TFrame")
        self.add_note_frame.pack(fill=tk.X, pady=5)
        
        self.add_note_button = ttk.Button(
            self.add_note_frame,
            text="New Note",
            style="Modern.TButton",
            command=self.on_new_note
        )
        self.add_note_button.pack(pady=5)
        
    def _on_notes_frame_configure(self, event) -> None:
        """Handle notes frame configuration changes"""
        self.notes_canvas.configure(scrollregion=self.notes_canvas.bbox("all"))
        
    def _on_notes_canvas_configure(self, event) -> None:
        """Handle notes canvas configuration changes"""
        # Update the width of the inner frame when the canvas changes
        canvas_width = event.width
        self.notes_canvas.itemconfig(self.notes_canvas_window, width=canvas_width)
        
    def _on_notes_mousewheel(self, event) -> None:
        """Handle mouse wheel scrolling on notes canvas"""
        self.notes_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def _create_status_bar(self) -> None:
        """Create status bar at the bottom of the window"""
        self.status_bar = ttk.Frame(self.main_frame, style="Toolbar.TFrame")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
        
        self.status_label = ttk.Label(
            self.status_bar, 
            text="Ready", 
            style="Status.TLabel",
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=5)
        
    def _bind_events(self) -> None:
        """Bind window events"""
        # Bind window focus events for auto-collapse
        self.window.bind("<FocusOut>", self._on_focus_out)
        self.window.bind("<FocusIn>", self._on_focus_in)
        
        # Bind mouse enter/leave for auto-collapse
        self.window.bind("<Enter>", self._on_mouse_enter)
        self.window.bind("<Leave>", self._on_mouse_leave)
        
    def _on_focus_out(self, event) -> None:
        """Handle window focus lost"""
        if self.auto_collapse_enabled and self.collapsible and self.visible:
            # Start timer to collapse
            if self.collapse_timer:
                self.window.after_cancel(self.collapse_timer)
                
            self.collapse_timer = self.window.after(
                self.auto_collapse_delay, 
                self._collapse_window
            )
            
    def _on_focus_in(self, event) -> None:
        """Handle window focus gained"""
        if self.auto_collapse_enabled and self.collapsible:
            # Cancel collapse timer if active
            if self.collapse_timer:
                self.window.after_cancel(self.collapse_timer)
                self.collapse_timer = None
                
            # Expand if collapsed
            if self.collapsed:
                self._expand_window()
                
    def _on_mouse_enter(self, event) -> None:
        """Handle mouse entering window"""
        if self.auto_collapse_enabled and self.collapsible:
            # Cancel collapse timer if active
            if self.collapse_timer:
                self.window.after_cancel(self.collapse_timer)
                self.collapse_timer = None
                
            # Expand if collapsed
            if self.collapsed:
                self._expand_window()
                
    def _on_mouse_leave(self, event) -> None:
        """Handle mouse leaving window"""
        if self.auto_collapse_enabled and self.collapsible and self.visible:
            # Start timer to collapse
            if self.collapse_timer:
                self.window.after_cancel(self.collapse_timer)
                
            self.collapse_timer = self.window.after(
                self.auto_collapse_delay, 
                self._collapse_window
            )
            
    def _collapse_window(self) -> None:
        """Collapse window to edge of screen"""
        if not self.visible or self.collapsed:
            return
            
        # Get current window geometry
        geometry = self.window.geometry()
        match = tk.re.match(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)', geometry)
        if not match:
            return
            
        width, height, x, y = map(int, match.groups())
        
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Determine collapse position
        position = self.auto_collapse_position
        
        # Store original geometry for expansion
        self.original_geometry = geometry
        
        # Calculate new position based on collapse direction
        if position == "right":
            new_x = screen_width - 10
            new_width = 10
            new_y = y
            new_height = height
        elif position == "left":
            new_x = 0
            new_width = 10
            new_y = y
            new_height = height
        elif position == "top":
            new_x = x
            new_width = width
            new_y = 0
            new_height = 10
        elif position == "bottom":
            new_x = x
            new_width = width
            new_y = screen_height - 10
            new_height = 10
        else:
            # Default to right
            new_x = screen_width - 10
            new_width = 10
            new_y = y
            new_height = height
            
        # Set new geometry
        self.window.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
        self.collapsed = True
        
    def _expand_window(self) -> None:
        """Expand window to original size"""
        if not self.collapsed:
            return
            
        # Restore original geometry if available
        if hasattr(self, "original_geometry") and self.original_geometry:
            self.window.geometry(self.original_geometry)
            
        self.collapsed = False
        
    def refresh_history(self) -> None:
        """Refresh clipboard history"""
        # Clear listbox
        self.history_listbox.delete(0, tk.END)
        
        # Get history from clipboard manager
        history = self.app.clipboard_manager.history
        
        # Add items to listbox in reverse order (newest first)
        for item in reversed(history):
            # Truncate long items for display
            display_text = str(item)
            if len(display_text) > 60:
                display_text = display_text[:57] + "..."
                
            self.history_listbox.insert(tk.END, display_text)
            
    def refresh_notes(self) -> None:
        """Refresh notes display"""
        # Clear all notes
        for widget in self.notes_inner_frame.winfo_children():
            widget.destroy()
            
        # Get notes from settings
        sticky_notes = self.app.settings.get_sticky_notes()
        regular_notes = self.app.settings.get_notes()
        
        # Add sticky notes first with label
        if sticky_notes:
            sticky_label = ttk.Label(
                self.notes_inner_frame,
                text="Pinned Notes",
                style="Modern.Title.TLabel"
            )
            sticky_label.pack(fill=tk.X, padx=5, pady=(10, 5))
            
            for note in sticky_notes:
                self._create_note_widget(note, True)
                
        # Add regular notes with label if there are any
        if regular_notes:
            regular_label = ttk.Label(
                self.notes_inner_frame,
                text="Notes",
                style="Modern.Title.TLabel"
            )
            regular_label.pack(fill=tk.X, padx=5, pady=(10, 5))
            
            for note in regular_notes:
                self._create_note_widget(note, False)
                
        # Update canvas scroll region
        self.notes_canvas.update_idletasks()
        self.notes_canvas.configure(scrollregion=self.notes_canvas.bbox("all"))
                
    def _create_note_widget(self, note: Dict, is_sticky: bool) -> None:
        """Create a note widget
        
        Args:
            note: Note data dictionary
            is_sticky: Whether this is a sticky note
        """
        note_id = note.get("id")
        content = note.get("content", "")
        created = note.get("created", {}).get("date", "")
        
        # Create note frame
        note_frame = ttk.Frame(
            self.notes_inner_frame,
            style="Modern.TLabelframe",
            borderwidth=1,
            relief=tk.SOLID
        )
        note_frame.pack(fill=tk.X, padx=5, pady=5, ipady=5)
        
        # Create top bar with tools
        top_bar = ttk.Frame(note_frame, style="Modern.TFrame")
        top_bar.pack(fill=tk.X, padx=2, pady=(2, 5))
        
        # Add sticky/unsticky button
        sticky_text = "📌" if not is_sticky else "📍"
        sticky_tip = "Pin Note" if not is_sticky else "Unpin Note"
        sticky_btn = ttk.Button(
            top_bar, 
            text=sticky_text,
            width=3,
            command=lambda nid=note_id: self.on_toggle_sticky(nid)
        )
        sticky_btn.pack(side=tk.LEFT, padx=2)
        
        # Add tools
        edit_btn = ttk.Button(
            top_bar, 
            text="✏️",
            width=3,
            command=lambda nid=note_id, c=content: self.on_edit_note(nid, c)
        )
        edit_btn.pack(side=tk.LEFT, padx=2)
        
        delete_btn = ttk.Button(
            top_bar, 
            text="🗑️",
            width=3,
            command=lambda nid=note_id: self.on_delete_note(nid)
        )
        delete_btn.pack(side=tk.LEFT, padx=2)
        
        # Add move buttons on the right
        move_frame = ttk.Frame(top_bar, style="Modern.TFrame")
        move_frame.pack(side=tk.RIGHT)
        
        top_btn = ttk.Button(
            move_frame, 
            text="⏫",
            width=3,
            command=lambda nid=note_id: self.on_move_note(nid, "top")
        )
        top_btn.pack(side=tk.LEFT, padx=1)
        
        up_btn = ttk.Button(
            move_frame, 
            text="🔼",
            width=3,
            command=lambda nid=note_id: self.on_move_note(nid, "up")
        )
        up_btn.pack(side=tk.LEFT, padx=1)
        
        down_btn = ttk.Button(
            move_frame, 
            text="🔽",
            width=3,
            command=lambda nid=note_id: self.on_move_note(nid, "down")
        )
        down_btn.pack(side=tk.LEFT, padx=1)
        
        bottom_btn = ttk.Button(
            move_frame, 
            text="⏬",
            width=3,
            command=lambda nid=note_id: self.on_move_note(nid, "bottom")
        )
        bottom_btn.pack(side=tk.LEFT, padx=1)
        
        # Create content area
        content_frame = ttk.Frame(note_frame, style="Modern.TFrame")
        content_frame.pack(fill=tk.X, expand=True, padx=5, pady=5)
        
        # Add content with overflow handling
        content_label = ttk.Label(
            content_frame,
            text=content,
            style="Modern.TLabel",
            wraplength=350  # Set wraplength to handle long text
        )
        content_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Add click handling for copy to clipboard
        content_label.bind(
            "<Button-1>", 
            lambda event, c=content, nid=note_id: self.on_note_click(c, nid)
        )
        
        # Add right-click context menu
        content_label.bind(
            "<Button-3>",
            lambda event, nid=note_id, c=content: self.on_note_right_click(event, nid, c)
        )
        
        # Add date/time in small text if available
        if created:
            date_label = ttk.Label(
                note_frame,
                text=f"Created: {created}",
                style="Status.TLabel",
                font=("Segoe UI", 8)
            )
            date_label.pack(fill=tk.X, padx=5, pady=(0, 5), anchor=tk.E)
        
    def on_note_click(self, content: str, note_id: str) -> None:
        """Handle note click - copy to clipboard
        
        Args:
            content: Note content to copy
            note_id: ID of the clicked note
        """
        # Copy to clipboard
        self.app.clipboard_manager.copy_to_clipboard(content)
        
        # Update last used timestamp if enabled
        self.app.settings.update_note_used(note_id)
        
        # Refresh notes to reflect any changes
        self.refresh_notes()
        
        # Update status
        self.status_label.config(text=f"Copied note to clipboard")
        
    def on_note_right_click(self, event, note_id: str, content: str) -> None:
        """Handle note right-click - show context menu
        
        Args:
            event: Mouse event
            note_id: ID of the clicked note
            content: Note content
        """
        # Create a popup menu
        popup_menu = tk.Menu(self.window, tearoff=0)
        popup_menu.add_command(label="Copy to Clipboard", 
                               command=lambda: self.on_note_click(content, note_id))
        popup_menu.add_separator()
        popup_menu.add_command(label="Edit", 
                               command=lambda: self.on_edit_note(note_id, content))
        popup_menu.add_command(label="Delete", 
                               command=lambda: self.on_delete_note(note_id))
        popup_menu.add_separator()
        popup_menu.add_command(label="Toggle Pin", 
                               command=lambda: self.on_toggle_sticky(note_id))
        
        # Display menu
        try:
            popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            popup_menu.grab_release()
    
    def on_toggle_sticky(self, note_id: str) -> None:
        """Toggle whether a note is sticky
        
        Args:
            note_id: ID of the note to toggle
        """
        result = self.app.settings.toggle_note_sticky(note_id)
        self.refresh_notes()
        
        status = "pinned" if result else "unpinned"
        self.status_label.config(text=f"Note {status}")
        
    def on_move_note(self, note_id: str, direction: str) -> None:
        """Move a note in a direction
        
        Args:
            note_id: ID of the note to move
            direction: Direction to move (up, down, top, bottom)
        """
        result = self.app.settings.move_note(note_id, direction)
        
        if result:
            self.refresh_notes()
            self.status_label.config(text=f"Note moved {direction}")
        
    def on_edit_note(self, note_id: str, current_content: str) -> None:
        """Edit a note
        
        Args:
            note_id: ID of the note to edit
            current_content: Current note content
        """
        # Show dialog to edit note
        new_content = simpledialog.askstring(
            "Edit Note",
            "Edit note content:",
            initialvalue=current_content,
            parent=self.window
        )
        
        if new_content is not None and new_content != current_content:
            # Update the note
            if self.app.update_note(note_id, new_content):
                self.status_label.config(text="Note updated")
            else:
                self.status_label.config(text="Failed to update note")
    
    def on_delete_note(self, note_id: str) -> None:
        """Delete a note
        
        Args:
            note_id: ID of the note to delete
        """
        # Confirm deletion if setting enabled
        if self.app.settings.get("general", "confirm_delete", True):
            if not messagebox.askyesno("Delete Note", 
                                     "Are you sure you want to delete this note?",
                                     parent=self.window):
                return
                
        # Delete the note
        if self.app.settings.delete_note(note_id):
            self.refresh_notes()
            self.status_label.config(text="Note deleted")
        else:
            self.status_label.config(text="Failed to delete note")
    
    def on_history_item_double_click(self, event) -> None:
        """Handle double-click on history item"""
        # Get selected item index
        selected_index = self.history_listbox.curselection()
        
        if not selected_index:
            return
            
        # Get actual item from clipboard history (accounting for reverse order)
        history = self.app.clipboard_manager.history
        real_index = len(history) - 1 - selected_index[0]
        
        if real_index < 0 or real_index >= len(history):
            return
            
        item = history[real_index]
        
        # Copy to clipboard
        self.app.clipboard_manager.copy_to_clipboard(item)
        
        # Update status
        self.status_label.config(text="Copied to clipboard")
        
        # Hide window after paste if enabled
        if self.app.settings.get("general", "hide_after_paste", True):
            self.hide()
        
    def on_history_item_right_click(self, event) -> None:
        """Handle right-click on history item"""
        # Get the item under the cursor
        item_index = self.history_listbox.nearest(event.y)
        self.history_listbox.selection_clear(0, tk.END)
        self.history_listbox.selection_set(item_index)
        
        # Get actual item from clipboard history (accounting for reverse order)
        history = self.app.clipboard_manager.history
        real_index = len(history) - 1 - item_index
        
        if real_index < 0 or real_index >= len(history):
            return
            
        item = history[real_index]
        
        # Create menu
        popup = tk.Menu(self.window, tearoff=0)
        popup.add_command(label="Copy to Clipboard", 
                         command=lambda: self._copy_history_item(real_index))
        popup.add_command(label="Save as Note", 
                         command=lambda: self._save_history_item_as_note(item))
        popup.add_separator()
        popup.add_command(label="Delete", 
                         command=lambda: self._delete_history_item(real_index))
        
        # Display menu
        try:
            popup.tk_popup(event.x_root, event.y_root)
        finally:
            popup.grab_release()
            
    def _copy_history_item(self, index: int) -> None:
        """Copy a history item to clipboard
        
        Args:
            index: Index of the item in the history list
        """
        history = self.app.clipboard_manager.history
        if 0 <= index < len(history):
            item = history[index]
            self.app.clipboard_manager.copy_to_clipboard(item)
            self.status_label.config(text="Copied to clipboard")
            
    def _save_history_item_as_note(self, content: str) -> None:
        """Save a history item as a note
        
        Args:
            content: Content to save as note
        """
        if self.app.add_note(content):
            self.notebook.select(1)  # Switch to notes tab
            self.status_label.config(text="Saved as note")
        else:
            self.status_label.config(text="Failed to save note")
            
    def _delete_history_item(self, index: int) -> None:
        """Delete a history item
        
        Args:
            index: Index of the item to delete
        """
        history = self.app.clipboard_manager.history
        if 0 <= index < len(history):
            # Request confirmation if enabled
            if self.app.settings.get("general", "confirm_delete", True):
                if not messagebox.askyesno("Delete Item", 
                                         "Are you sure you want to delete this item?",
                                         parent=self.window):
                    return
                    
            # Delete the item
            del self.app.clipboard_manager.history[index]
            self.refresh_history()
            self.status_label.config(text="Item deleted")
    
    def on_new_note(self) -> None:
        """Create a new note"""
        # Show dialog to enter note content
        content = simpledialog.askstring(
            "New Note",
            "Enter note content:",
            parent=self.window
        )
        
        if content:
            if self.app.add_note(content):
                self.notebook.select(1)  # Switch to notes tab
                self.status_label.config(text="Note created")
            else:
                self.status_label.config(text="Failed to create note")
    
    def on_settings(self) -> None:
        """Open settings dialog"""
        self.status_label.config(text="Opening settings...")
        
        # Create settings dialog - a simple implementation
        settings_window = tk.Toplevel(self.window)
        settings_window.title("Settings")
        settings_window.geometry("500x400")
        settings_window.transient(self.window)
        settings_window.grab_set()
        
        # Add settings notebook for tabs
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General settings tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        # UI settings tab
        ui_frame = ttk.Frame(notebook)
        notebook.add(ui_frame, text="Appearance")
        
        # Hotkeys tab
        hotkeys_frame = ttk.Frame(notebook)
        notebook.add(hotkeys_frame, text="Hotkeys")
        
        # Auto-collapse tab
        collapse_frame = ttk.Frame(notebook)
        notebook.add(collapse_frame, text="Auto-Collapse")
        
        # Fill general settings
        row = 0
        ttk.Label(general_frame, text="Clipboard Settings", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky="w", padx=5, pady=(10, 5)
        )
        row += 1
        
        # Max history items
        ttk.Label(general_frame, text="Max history items:").grid(
            row=row, column=0, sticky="w", padx=5, pady=2
        )
        max_history_var = tk.IntVar(value=self.app.settings.get("general", "max_history_items", 100))
        ttk.Spinbox(
            general_frame, 
            from_=10, 
            to=1000, 
            increment=10, 
            textvariable=max_history_var
        ).grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        
        # Poll interval
        ttk.Label(general_frame, text="Clipboard poll interval (s):").grid(
            row=row, column=0, sticky="w", padx=5, pady=2
        )
        poll_interval_var = tk.DoubleVar(
            value=self.app.settings.get("general", "clipboard_poll_interval", 0.5)
        )
        ttk.Spinbox(
            general_frame, 
            from_=0.1, 
            to=5.0, 
            increment=0.1, 
            textvariable=poll_interval_var,
            format="%.1f"
        ).grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        
        # Startup settings section
        ttk.Label(general_frame, text="Startup Settings", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky="w", padx=5, pady=(10, 5)
        )
        row += 1
        
        # Start minimized
        start_minimized_var = tk.BooleanVar(
            value=self.app.settings.get("general", "start_minimized", False)
        )
        ttk.Checkbutton(
            general_frame, 
            text="Start minimized", 
            variable=start_minimized_var
        ).grid(row=row, column=0, sticky="w", padx=5, pady=2, columnspan=2)
        row += 1
        
        # Start with system
        start_with_system_var = tk.BooleanVar(
            value=self.app.settings.get("general", "start_with_system", False)
        )
        ttk.Checkbutton(
            general_frame, 
            text="Start with system", 
            variable=start_with_system_var
        ).grid(row=row, column=0, sticky="w", padx=5, pady=2, columnspan=2)
        row += 1
        
        # Notes settings section
        ttk.Label(general_frame, text="Notes Settings", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky="w", padx=5, pady=(10, 5)
        )
        row += 1
        
        # Last used to top
        last_used_to_top_var = tk.BooleanVar(
            value=self.app.settings.get("general", "last_used_to_top", True)
        )
        ttk.Checkbutton(
            general_frame, 
            text="Move last used note to top", 
            variable=last_used_to_top_var
        ).grid(row=row, column=0, sticky="w", padx=5, pady=2, columnspan=2)
        row += 1
        
        # Fill UI settings tab
        row = 0
        ttk.Label(ui_frame, text="Window Settings", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky="w", padx=5, pady=(10, 5)
        )
        row += 1
        
        # Opacity
        ttk.Label(ui_frame, text="Window opacity:").grid(
            row=row, column=0, sticky="w", padx=5, pady=2
        )
        opacity_var = tk.DoubleVar(value=self.app.settings.get("ui", "opacity", 0.98))
        ttk.Scale(
            ui_frame,
            from_=0.5,
            to=1.0,
            variable=opacity_var,
            orient=tk.HORIZONTAL,
            length=200
        ).grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        
        # Always on top
        always_on_top_var = tk.BooleanVar(
            value=self.app.settings.get("ui", "always_on_top", False)
        )
        ttk.Checkbutton(
            ui_frame, 
            text="Always on top", 
            variable=always_on_top_var
        ).grid(row=row, column=0, sticky="w", padx=5, pady=2, columnspan=2)
        row += 1
        
        # Fill auto-collapse tab
        row = 0
        ttk.Label(collapse_frame, text="Auto-Collapse Settings", font=("Segoe UI", 10, "bold")).grid(
            row=row, column=0, sticky="w", padx=5, pady=(10, 5)
        )
        row += 1
        
        # Enable auto-collapse
        enable_collapse_var = tk.BooleanVar(
            value=self.app.settings.get("ui", "enable_auto_collapse", True)
        )
        ttk.Checkbutton(
            collapse_frame, 
            text="Enable auto-collapse", 
            variable=enable_collapse_var
        ).grid(row=row, column=0, sticky="w", padx=5, pady=2, columnspan=2)
        row += 1
        
        # Collapse position
        ttk.Label(collapse_frame, text="Collapse position:").grid(
            row=row, column=0, sticky="w", padx=5, pady=2
        )
        position_var = tk.StringVar(
            value=self.app.settings.get("general", "auto_collapse", {}).get("position", "right")
        )
        ttk.Combobox(
            collapse_frame, 
            textvariable=position_var,
            values=["right", "left", "top", "bottom"],
            state="readonly",
            width=15
        ).grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        
        # Collapse delay
        ttk.Label(collapse_frame, text="Collapse delay (s):").grid(
            row=row, column=0, sticky="w", padx=5, pady=2
        )
        delay_var = tk.DoubleVar(
            value=self.app.settings.get("general", "auto_collapse", {}).get("delay_seconds", 1.5)
        )
        ttk.Spinbox(
            collapse_frame, 
            from_=0.5, 
            to=10.0, 
            increment=0.5, 
            textvariable=delay_var,
            format="%.1f"
        ).grid(row=row, column=1, sticky="w", padx=5, pady=2)
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_settings():
            # Save all settings
            # General settings
            self.app.settings.set("general", "max_history_items", max_history_var.get())
            self.app.settings.set("general", "clipboard_poll_interval", poll_interval_var.get())
            self.app.settings.set("general", "start_minimized", start_minimized_var.get())
            self.app.settings.set("general", "start_with_system", start_with_system_var.get())
            self.app.settings.set("general", "last_used_to_top", last_used_to_top_var.get())
            
            # UI settings
            self.app.settings.set("ui", "opacity", opacity_var.get())
            self.app.settings.set("ui", "always_on_top", always_on_top_var.get())
            
            # Auto-collapse settings
            self.app.settings.set("ui", "enable_auto_collapse", enable_collapse_var.get())
            auto_collapse = self.app.settings.get("general", "auto_collapse", {})
            auto_collapse["position"] = position_var.get()
            auto_collapse["delay_seconds"] = delay_var.get()
            self.app.settings.set("general", "auto_collapse", auto_collapse)
            
            # Save settings
            self.app.settings.save()
            
            # Apply changes
            self.window.attributes('-topmost', always_on_top_var.get())
            self.window.attributes('-alpha', opacity_var.get())
            self.auto_collapse_enabled = enable_collapse_var.get()
            self.auto_collapse_position = position_var.get()
            self.auto_collapse_delay = delay_var.get() * 1000
            
            # Close dialog
            settings_window.destroy()
            self.status_label.config(text="Settings saved")
            
            # Restart monitoring with new interval
            self.app.clipboard_manager.stop_monitoring()
            self.app.clipboard_manager.start_monitoring(interval=poll_interval_var.get())
            
        ttk.Button(
            button_frame, 
            text="Save", 
            command=save_settings,
            style="Modern.TButton"
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=settings_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Set window position relative to main window
        settings_window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - settings_window.winfo_width()) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - settings_window.winfo_height()) // 2
        settings_window.geometry(f"+{max(0, x)}+{max(0, y)}")
        
    def on_plugins(self) -> None:
        """Open plugins dialog"""
        # Create plugins dialog
        plugins_window = tk.Toplevel(self.window)
        plugins_window.title("Plugins")
        plugins_window.geometry("500x400")
        plugins_window.transient(self.window)
        plugins_window.grab_set()
        
        # Get plugins list
        plugins = self.app.plugin_manager.get_plugins()
        enabled_plugins = self.app.settings.get("plugins", "enabled", [])
        
        # Create main frame
        main_frame = ttk.Frame(plugins_window, style="Modern.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        ttk.Label(main_frame, text="Available Plugins", font=("Segoe UI", 12, "bold")).pack(
            fill=tk.X, pady=(0, 10)
        )
        
        # Create listbox with scrollbar to show plugins
        list_frame = ttk.Frame(main_frame, style="Modern.TFrame")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        plugins_list = tk.Listbox(
            list_frame,
            bg=self.app.theme_manager.themes["light"]["colors"]["background"],
            fg=self.app.theme_manager.themes["light"]["colors"]["foreground"],
            selectbackground=self.app.theme_manager.themes["light"]["colors"]["accent"],
            selectforeground="#FFFFFF",
            font=self.app.theme_manager.themes["light"]["fonts"]["main"],
            bd=1,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        plugins_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=plugins_list.yview)
        
        # Add plugins to listbox
        for plugin_id, plugin_info in plugins.items():
            plugins_list.insert(tk.END, f"{plugin_info['name']} ({plugin_id})")
            
        # Add details frame
        details_frame = ttk.LabelFrame(main_frame, text="Plugin Details", style="Modern.TLabelframe")
        details_frame.pack(fill=tk.X, pady=10)
        
        name_var = tk.StringVar()
        version_var = tk.StringVar()
        author_var = tk.StringVar()
        description_var = tk.StringVar()
        
        # Plugin details
        ttk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(details_frame, textvariable=name_var).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Version:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(details_frame, textvariable=version_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Author:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(details_frame, textvariable=author_var).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(details_frame, text="Description:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(details_frame, textvariable=description_var, wraplength=300).grid(
            row=3, column=1, sticky="w", padx=5, pady=2
        )
        
        # Enable/disable button
        enable_var = tk.BooleanVar(value=False)
        enable_button = ttk.Button(
            main_frame, 
            text="Enable",
            style="Modern.TButton"
        )
        enable_button.pack(side=tk.LEFT, pady=10)
        
        # Status label
        status_label = ttk.Label(main_frame, text="", style="Status.TLabel")
        status_label.pack(side=tk.RIGHT, pady=10)
        
        # Plugin selection handler
        def on_plugin_select(event):
            selection = plugins_list.curselection()
            if not selection:
                return
                
            index = selection[0]
            if index < 0 or index >= len(plugins):
                return
                
            # Get plugin ID from selection
            plugin_id = list(plugins.keys())[index]
            plugin_info = plugins[plugin_id]
            
            # Update details
            name_var.set(plugin_info["name"])
            version_var.set(plugin_info["version"])
            author_var.set(plugin_info["author"])
            description_var.set(plugin_info["description"])
            
            # Update enable button
            is_enabled = plugin_id in enabled_plugins
            enable_var.set(is_enabled)
            enable_button.config(text="Disable" if is_enabled else "Enable")
            
            def toggle_plugin():
                nonlocal is_enabled
                if is_enabled:
                    # Disable plugin
                    self.app.plugin_manager.disable_plugin(plugin_id)
                    enabled_plugins.remove(plugin_id)
                    is_enabled = False
                    status_label.config(text=f"{plugin_info['name']} disabled")
                else:
                    # Enable plugin
                    if self.app.plugin_manager.enable_plugin(plugin_id):
                        enabled_plugins.append(plugin_id)
                        is_enabled = True
                        status_label.config(text=f"{plugin_info['name']} enabled")
                    else:
                        status_label.config(text=f"Failed to enable {plugin_info['name']}")
                        return
                
                # Update settings
                self.app.settings.set("plugins", "enabled", enabled_plugins)
                self.app.settings.save()
                
                # Update button text
                enable_button.config(text="Disable" if is_enabled else "Enable")
                
            # Update button command
            enable_button.config(command=toggle_plugin)
            
        plugins_list.bind("<<ListboxSelect>>", on_plugin_select)
        
        # Close button
        ttk.Button(
            main_frame, 
            text="Close",
            command=plugins_window.destroy
        ).pack(side=tk.BOTTOM, pady=10)
        
        # Set window position relative to main window
        plugins_window.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - plugins_window.winfo_width()) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - plugins_window.winfo_height()) // 2
        plugins_window.geometry(f"+{max(0, x)}+{max(0, y)}")
        
    def refresh_content(self) -> None:
        """Refresh all content"""
        self.refresh_history()
        self.refresh_notes()
        
    def show(self) -> None:
        """Show the window"""
        # Deiconify window if minimized
        self.window.deiconify()
        
        # Bring to front
        self.window.lift()
        self.window.focus_force()
        
        # Expand if collapsed
        if self.collapsed:
            self._expand_window()
            
        # Refresh content
        self.refresh_content()
        
        # Update state
        self.visible = True
        
    def hide(self) -> None:
        """Hide the window"""
        self.window.withdraw()
        self.visible = False
        
        # Cancel any pending collapse timer
        if self.collapse_timer:
            self.window.after_cancel(self.collapse_timer)
            self.collapse_timer = None
            
    def toggle_visibility(self) -> None:
        """Toggle window visibility"""
        if self.visible:
            self.hide()
        else:
            self.show()
            
    def on_window_close(self) -> None:
        """Handle window close event"""
        self.app.on_close()
        
    def destroy(self) -> None:
        """Clean up and destroy the window"""
        # Cancel any pending timers
        if self.collapse_timer:
            self.window.after_cancel(self.collapse_timer)
            self.collapse_timer = None
            
        # Remove from window list if needed
        if self in self.app.windows:
            self.app.windows.remove(self)
            
        # Destroy window
        if self.window and self.window.winfo_exists():
            self.window.destroy()
