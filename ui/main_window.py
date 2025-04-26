
"""
Main window of the ClipScribe Plus application.
"""
import logging
import os  # Add missing import
import tkinter as tk
from tkinter import ttk, messagebox
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
        self._create_modern_menu()
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
        
        # Disable maximize button
        self.root.resizable(True, True)
        self.root.attributes("-fullscreen", False)
        # Apply Mica Material effect (Windows 11)
        if hasattr(self.root, "attributes"):
            try:
                # For Windows 11, try to enable Mica effect
                self.root.attributes("-transparentcolor", "")
                # Enable semi-transparent blur effect (simulating Mica)
                self.root.attributes("-alpha", 0.98)
            except Exception as e:
                logger.warning(f"Could not apply Mica effect: {str(e)}")
        
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
        
    def _create_modern_menu(self) -> None:
        """Create a modern menu bar using frames instead of traditional menu"""
        self.modern_menu_frame = ttk.Frame(self.root, style="Modern.TFrame")
        
        # Create menu buttons with modern style
        self.file_btn = ttk.Button(
            self.modern_menu_frame, 
            text="File",
            style="Modern.MenuButton.TButton",
            command=self._show_file_menu
        )
        
        self.edit_btn = ttk.Button(
            self.modern_menu_frame, 
            text="Edit",
            style="Modern.MenuButton.TButton",
            command=self._show_edit_menu
        )
        
        self.view_btn = ttk.Button(
            self.modern_menu_frame, 
            text="View",
            style="Modern.MenuButton.TButton",
            command=self._show_view_menu
        )
        
        self.plugins_btn = ttk.Button(
            self.modern_menu_frame, 
            text="Plugins",
            style="Modern.MenuButton.TButton",
            command=self._open_plugins
        )
        
        self.help_btn = ttk.Button(
            self.modern_menu_frame, 
            text="Help",
            style="Modern.MenuButton.TButton",
            command=self._show_help_menu
        )
        
        # Application title in the center
        self.title_label = ttk.Label(
            self.modern_menu_frame,
            text="ClipScribe Plus",
            style="Modern.Title.TLabel"
        )
        
        # Pack buttons to the left
        self.file_btn.pack(side=tk.LEFT, padx=(10, 5))
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        self.view_btn.pack(side=tk.LEFT, padx=5)
        self.plugins_btn.pack(side=tk.LEFT, padx=5)
        self.help_btn.pack(side=tk.LEFT, padx=5)
        
        # Pack title to the center (will be positioned better in _setup_layout)
        self.title_label.pack(side=tk.LEFT, expand=True, padx=5)
        
        # Also create the traditional menu for backup/functionality
        self._create_menu()
        
    def _create_menu(self) -> None:
        """Create the traditional menu bar (hidden by default but functional)"""
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
        
    def _show_file_menu(self) -> None:
        """Show file menu dropdown"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="New Window", command=self._new_window)
        menu.add_separator()
        menu.add_command(label="Settings", command=self._open_settings)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.app.on_close)
        
        # Position menu under the button
        x = self.file_btn.winfo_rootx()
        y = self.file_btn.winfo_rooty() + self.file_btn.winfo_height()
        menu.tk_popup(x, y)
        
    def _show_edit_menu(self) -> None:
        """Show edit menu dropdown"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Clear Clipboard History", command=self._clear_history)
        menu.add_separator()
        menu.add_command(label="Undo", command=self._undo)
        menu.add_command(label="Redo", command=self._redo)
        
        # Position menu under the button
        x = self.edit_btn.winfo_rootx()
        y = self.edit_btn.winfo_rooty() + self.edit_btn.winfo_height()
        menu.tk_popup(x, y)
        
    def _show_view_menu(self) -> None:
        """Show view menu dropdown"""
        menu = tk.Menu(self.root, tearoff=0)
        
        # Theme submenu
        theme_menu = tk.Menu(menu, tearoff=0)
        theme_menu.add_command(label="Light", command=lambda: self._change_theme("light"))
        theme_menu.add_command(label="Dark", command=lambda: self._change_theme("dark"))
        theme_menu.add_command(label="System", command=lambda: self._change_theme("system"))
        theme_menu.add_command(label="High Contrast", command=lambda: self._change_theme("high_contrast"))
        menu.add_cascade(label="Theme", menu=theme_menu)
        
        menu.add_separator()
        menu.add_checkbutton(label="Always on Top", 
                             variable=self.always_on_top_var,
                             command=self._toggle_always_on_top)
        menu.add_command(label="Opacity...", command=self._show_opacity_dialog)
        
        # Position menu under the button
        x = self.view_btn.winfo_rootx()
        y = self.view_btn.winfo_rooty() + self.view_btn.winfo_height()
        menu.tk_popup(x, y)
        
    def _show_help_menu(self) -> None:
        """Show help menu dropdown"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Documentation", command=self._open_docs)
        menu.add_command(label="About", command=self._show_about)
        
        # Position menu under the button
        x = self.help_btn.winfo_rootx()
        y = self.help_btn.winfo_rooty() + self.help_btn.winfo_height()
        menu.tk_popup(x, y)
        
    def _create_components(self) -> None:
        """Create UI components"""
        # Main frame
        self.main_frame = ttk.Frame(self.root, style="Main.TFrame")
        
        # Toolbar
        self.toolbar = ttk.Frame(self.main_frame, style="Toolbar.TFrame")
        
        # New window button
        self.new_window_btn = ttk.Button(
            self.toolbar, 
            text="New Window",
            style="Modern.TButton",
            command=self._new_window
        )
        
        # Search box
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            self.toolbar, 
            textvariable=self.search_var,
            width=30,
            style="Modern.TEntry"
        )
        
        # Clear history button
        self.clear_btn = ttk.Button(
            self.toolbar, 
            text="Clear",
            style="Modern.TButton",
            command=self._clear_history
        )
        
        # Notes section
        self.notes_frame = ttk.LabelFrame(self.main_frame, text="Notes", style="Modern.TLabelframe")
        self.notes_list = tk.Listbox(
            self.notes_frame,
            selectmode=tk.SINGLE,
            activestyle='dotbox',
            font=('Segoe UI', 10),
            bg='#2C2C2C',  # Dark background for notes
            fg='#FFFFFF',  # White text
            highlightbackground='#3C3C3C',
            highlightcolor='#3C3C3C',
            selectbackground='#505050',
            selectforeground='#FFFFFF',
            height=5
        )
        self.notes_scrollbar = ttk.Scrollbar(
            self.notes_frame,
            orient=tk.VERTICAL,
            command=self.notes_list.yview
        )
        self.notes_list.config(yscrollcommand=self.notes_scrollbar.set)
        
        # Notes buttons
        self.notes_btn_frame = ttk.Frame(self.notes_frame, style="Modern.TFrame")
        self.add_note_btn = ttk.Button(
            self.notes_btn_frame,
            text="Add Note",
            style="Modern.TButton",
            command=self._add_note
        )
        self.move_up_btn = ttk.Button(
            self.notes_btn_frame,
            text="↑",
            width=2,
            style="Modern.TButton",
            command=self._move_note_up
        )
        self.move_down_btn = ttk.Button(
            self.notes_btn_frame,
            text="↓",
            width=2,
            style="Modern.TButton",
            command=self._move_note_down
        )
        self.move_top_btn = ttk.Button(
            self.notes_btn_frame,
            text="⮝",
            width=2,
            style="Modern.TButton",
            command=self._move_note_top
        )
        self.move_bottom_btn = ttk.Button(
            self.notes_btn_frame,
            text="⮟",
            width=2,
            style="Modern.TButton",
            command=self._move_note_bottom
        )
        self.pin_note_btn = ttk.Button(
            self.notes_btn_frame,
            text="📌",
            width=2,
            style="Modern.TButton",
            command=self._toggle_pin_note
        )
        
        # Clipboard list frame
        self.list_frame = ttk.LabelFrame(self.main_frame, text="Clipboard History", style="Modern.TLabelframe")
        
        # Create a listbox with scrollbar for clipboard items
        self.clip_list = tk.Listbox(
            self.list_frame,
            selectmode=tk.SINGLE,
            activestyle='dotbox',
            font=('Segoe UI', 10),
            bg='#2C2C2C',  # Dark background
            fg='#FFFFFF',  # White text
            highlightbackground='#3C3C3C',
            highlightcolor='#3C3C3C',
            selectbackground='#505050',
            selectforeground='#FFFFFF',
            height=15
        )
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(
            self.list_frame,
            orient=tk.VERTICAL,
            command=self.clip_list.yview,
            style="Modern.Vertical.TScrollbar"
        )
        self.clip_list.config(yscrollcommand=self.scrollbar.set)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            anchor=tk.W,
            padding=(5, 2),
            style="Status.TLabel"
        )
        
        # Clipboard content preview frame
        self.preview_frame = ttk.LabelFrame(
            self.main_frame,
            text="Preview",
            padding=(5, 5),
            style="Modern.TLabelframe"
        )
        
        # Text widget for content preview
        self.preview_text = tk.Text(
            self.preview_frame,
            wrap=tk.WORD,
            height=5,
            state=tk.DISABLED,
            bg='#2C2C2C',  # Dark background
            fg='#FFFFFF',  # White text
            insertbackground='#FFFFFF',  # Cursor color
            highlightbackground='#3C3C3C',
            highlightcolor='#3C3C3C',
        )
        
        # Auto-collapse corner indicators
        self.collapse_indicators = {}
        for pos in ["top", "bottom", "left", "right"]:
            indicator = ttk.Frame(self.root, width=40, height=10, style="Indicator.TFrame")
            if pos == "top":
                indicator.place(relx=0.5, rely=0, anchor=tk.N, width=80, height=5)
            elif pos == "bottom":
                indicator.place(relx=0.5, rely=1, anchor=tk.S, width=80, height=5)
            elif pos == "left":
                indicator.place(relx=0, rely=0.5, anchor=tk.W, width=5, height=80)
            elif pos == "right":
                indicator.place(relx=1, rely=0.5, anchor=tk.E, width=5, height=80)
            indicator.bind("<Enter>", lambda e, p=pos: self._show_collapse_hint(p))
            indicator.bind("<Leave>", self._hide_collapse_hint)
            indicator.bind("<Button-1>", lambda e, p=pos: self._collapse_to_edge(p))
            self.collapse_indicators[pos] = indicator
        
    def _setup_layout(self) -> None:
        """Set up the UI layout"""
        # Configure root to expand components
        self.root.grid_rowconfigure(0, weight=0)  # Menu doesn't expand
        self.root.grid_rowconfigure(1, weight=1)  # Main content expands
        self.root.grid_columnconfigure(0, weight=1)
        
        # Modern menu at the top
        self.modern_menu_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # Main frame fills the window
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Clipboard list expands
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Toolbar at the top
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.new_window_btn.pack(side=tk.LEFT, padx=5)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Notes section below toolbar
        self.notes_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.notes_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.notes_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Notes buttons
        self.notes_btn_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
        self.add_note_btn.pack(side=tk.TOP, pady=2)
        self.move_up_btn.pack(side=tk.TOP, pady=2)
        self.move_down_btn.pack(side=tk.TOP, pady=2)
        self.move_top_btn.pack(side=tk.TOP, pady=2)
        self.move_bottom_btn.pack(side=tk.TOP, pady=2)
        self.pin_note_btn.pack(side=tk.TOP, pady=2)
        
        # Clipboard list in the middle
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        
        self.clip_list.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Preview frame
        self.preview_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar at the bottom
        self.status_bar.grid(row=4, column=0, sticky="ew")
        
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
        
        # Notes list events
        self.notes_list.bind("<<ListboxSelect>>", self._on_note_selected)
        self.notes_list.bind("<Button-3>", self._show_note_context_menu)
        
        # Register clipboard change listener
        self.app.clipboard_manager.add_clipboard_change_listener(
            self._on_clipboard_changed
        )
        
    # Note functionality
    def _add_note(self) -> None:
        """Add a new note"""
        # Get selected clipboard item if any
        selection = self.clip_list.curselection()
        content = ""
        
        if selection:
            index = selection[0]
            history_index = len(self.app.clipboard_manager.history) - 1 - index
            
            if 0 <= history_index < len(self.app.clipboard_manager.history):
                item = self.app.clipboard_manager.history[history_index]
                if item.content_type == 'text':
                    content = item.content
        
        # Create a dialog for entering note text
        note_dialog = tk.Toplevel(self.root)
        note_dialog.title("Add Note")
        note_dialog.geometry("400x300")
        note_dialog.transient(self.root)
        note_dialog.grab_set()
        
        # Make sure dialog follows dark theme
        note_dialog.configure(bg='#2C2C2C')
        
        # Text entry
        note_frame = ttk.Frame(note_dialog, style="Modern.TFrame")
        note_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        note_entry = tk.Text(
            note_frame,
            wrap=tk.WORD,
            bg='#2C2C2C',
            fg='#FFFFFF',
            insertbackground='#FFFFFF',
            highlightbackground='#3C3C3C',
            highlightcolor='#3C3C3C',
        )
        note_entry.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        note_entry.insert(tk.END, content)
        
        # Buttons
        btn_frame = ttk.Frame(note_dialog, style="Modern.TFrame")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_note():
            note_text = note_entry.get(1.0, tk.END).strip()
            if note_text:
                # Add to notes list
                self.notes_list.insert(tk.END, note_text[:50] + ("..." if len(note_text) > 50 else ""))
                # Save notes to settings or file
                self._save_notes()
                note_dialog.destroy()
        
        save_btn = ttk.Button(
            btn_frame,
            text="Save",
            style="Modern.TButton",
            command=save_note
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancel",
            style="Modern.TButton",
            command=note_dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Focus the entry
        note_entry.focus_set()
    
    def _move_note_up(self) -> None:
        """Move selected note up in the list"""
        selection = self.notes_list.curselection()
        if not selection or selection[0] == 0:
            return
            
        index = selection[0]
        text = self.notes_list.get(index)
        
        # Check if note is pinned
        is_pinned = text.startswith("📌 ")
        
        # Delete and reinsert
        self.notes_list.delete(index)
        self.notes_list.insert(index - 1, text)
        self.notes_list.selection_set(index - 1)
        self.notes_list.activate(index - 1)
        self._save_notes()
    
    def _move_note_down(self) -> None:
        """Move selected note down in the list"""
        selection = self.notes_list.curselection()
        if not selection or selection[0] == self.notes_list.size() - 1:
            return
            
        index = selection[0]
        text = self.notes_list.get(index)
        
        # Delete and reinsert
        self.notes_list.delete(index)
        self.notes_list.insert(index + 1, text)
        self.notes_list.selection_set(index + 1)
        self.notes_list.activate(index + 1)
        self._save_notes()
    
    def _move_note_top(self) -> None:
        """Move selected note to top of the list"""
        selection = self.notes_list.curselection()
        if not selection:
            return
            
        index = selection[0]
        text = self.notes_list.get(index)
        
        # Find the proper insertion point (after pinned notes)
        insertion_point = 0
        for i in range(self.notes_list.size()):
            if self.notes_list.get(i).startswith("📌 "):
                insertion_point = i + 1
        
        # Don't move if already at correct position
        if index == insertion_point:
            return
        
        # Delete and reinsert
        self.notes_list.delete(index)
        self.notes_list.insert(insertion_point, text)
        self.notes_list.selection_set(insertion_point)
        self.notes_list.activate(insertion_point)
        self._save_notes()
    
    def _move_note_bottom(self) -> None:
        """Move selected note to bottom of the list"""
        selection = self.notes_list.curselection()
        if not selection:
            return
            
        index = selection[0]
        text = self.notes_list.get(index)
        
        # Delete and reinsert
        self.notes_list.delete(index)
        self.notes_list.insert(tk.END, text)
        self.notes_list.selection_set(self.notes_list.size() - 1)
        self.notes_list.activate(self.notes_list.size() - 1)
        self._save_notes()
    
    def _toggle_pin_note(self) -> None:
        """Toggle pin status of selected note"""
        selection = self.notes_list.curselection()
        if not selection:
            return
            
        index = selection[0]
        text = self.notes_list.get(index)
        
        # Check if already pinned
        if text.startswith("📌 "):
            # Unpin
            text = text[2:].strip()  # Remove pin emoji
            self.notes_list.delete(index)
            self.notes_list.insert(index, text)
            self.notes_list.selection_set(index)
        else:
            # Pin and move to top
            self.notes_list.delete(index)
            new_text = "📌 " + text
            self.notes_list.insert(0, new_text)
            self.notes_list.selection_set(0)
        
        self._save_notes()
    
    def _save_notes(self) -> None:
        """Save notes to settings"""
        notes = []
        for i in range(self.notes_list.size()):
            notes.append(self.notes_list.get(i))
        
        # Save to settings
        self.app.settings.set("notes", "items", notes)
        self.app.settings.save()
    
    def _load_notes(self) -> None:
        """Load notes from settings"""
        notes = self.app.settings.get("notes", "items", [])
        
        for note in notes:
            self.notes_list.insert(tk.END, note)
    
    def _on_note_selected(self, event) -> None:
        """Handle note selection"""
        selection = self.notes_list.curselection()
        if not selection:
            return
            
        # Display note in preview
        index = selection[0]
        text = self.notes_list.get(index)
        
        # Remove pin marker for display
        if text.startswith("📌 "):
            text = text[2:].strip()
        
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, text)
        self.preview_text.config(state=tk.DISABLED)
    
    def _show_note_context_menu(self, event) -> None:
        """Show context menu for notes"""
        index = self.notes_list.nearest(event.y)
        if index < 0 or index >= self.notes_list.size():
            return
            
        self.notes_list.selection_clear(0, tk.END)
        self.notes_list.selection_set(index)
        self.notes_list.activate(index)
        self._on_note_selected(None)
        
        note_text = self.notes_list.get(index)
        is_pinned = note_text.startswith("📌 ")
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0, bg='#2C2C2C', fg='#FFFFFF', activebackground='#505050')
        context_menu.add_command(
            label="Edit Note", 
            command=lambda: self._edit_note(index)
        )
        context_menu.add_command(
            label="Delete Note", 
            command=lambda: self._delete_note(index)
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="Move Up", 
            command=self._move_note_up
        )
        context_menu.add_command(
            label="Move Down", 
            command=self._move_note_down
        )
        context_menu.add_command(
            label="Move to Top", 
            command=self._move_note_top
        )
        context_menu.add_command(
            label="Move to Bottom", 
            command=self._move_note_bottom
        )
        context_menu.add_separator()
        pin_label = "Unpin Note" if is_pinned else "Pin Note"
        context_menu.add_command(
            label=pin_label,
            command=self._toggle_pin_note
        )
        
        # Display the menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _edit_note(self, index) -> None:
        """Edit a note"""
        if index < 0 or index >= self.notes_list.size():
            return
        
        note_text = self.notes_list.get(index)
        is_pinned = note_text.startswith("📌 ")
        
        # Remove pin marker for editing
        if is_pinned:
            note_text = note_text[2:].strip()
        
        # Create edit dialog
        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Edit Note")
        edit_dialog.geometry("400x300")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        
        # Make sure dialog follows dark theme
        edit_dialog.configure(bg='#2C2C2C')
        
        # Text entry
        edit_frame = ttk.Frame(edit_dialog, style="Modern.TFrame")
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        edit_entry = tk.Text(
            edit_frame,
            wrap=tk.WORD,
            bg='#2C2C2C',
            fg='#FFFFFF',
            insertbackground='#FFFFFF',
            highlightbackground='#3C3C3C',
            highlightcolor='#3C3C3C',
        )
        edit_entry.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        edit_entry.insert(tk.END, note_text)
        
        # Buttons
        btn_frame = ttk.Frame(edit_dialog, style="Modern.TFrame")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_edit():
            new_text = edit_entry.get(1.0, tk.END).strip()
            if new_text:
                # Update notes list
                if is_pinned:
                    new_text = "📌 " + new_text
                    
                self.notes_list.delete(index)
                self.notes_list.insert(index, new_text)
                self.notes_list.selection_set(index)
                self._save_notes()
                edit_dialog.destroy()
        
        save_btn = ttk.Button(
            btn_frame,
            text="Save",
            style="Modern.TButton",
            command=save_edit
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancel",
            style="Modern.TButton",
            command=edit_dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Focus the entry
        edit_entry.focus_set()
    
    def _delete_note(self, index) -> None:
        """Delete a note"""
        if index < 0 or index >= self.notes_list.size():
            return
            
        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Delete this note?",
            parent=self.root
        )
        
        if confirm:
            self.notes_list.delete(index)
            self._save_notes()
    
    # Collapse functionality
    def _show_collapse_hint(self, position) -> None:
        """Show hint for collapsing the window"""
        self.status_var.set(f"Click to collapse to {position}")
        
    def _hide_collapse_hint(self, event=None) -> None:
        """Hide collapse hint"""
        self.status_var.set("Ready")
        
    def _collapse_to_edge(self, position) -> None:
        """Collapse window to screen edge"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Save current size
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        
        # Store dimensions for restoring later
        self.root.collapse_restore = {
            "width": current_width,
            "height": current_height,
            "position": self.root.geometry().split("+")[1:]
        }
        
        # Calculate new position and size
        if position == "top":
            self.root.geometry(f"{current_width}x10+{int((screen_width-current_width)/2)}+0")
        elif position == "bottom":
            self.root.geometry(f"{current_width}x10+{int((screen_width-current_width)/2)}+{screen_height-10}")
        elif position == "left":
            self.root.geometry(f"10x{current_height}+0+{int((screen_height-current_height)/2)}")
        elif position == "right":
            self.root.geometry(f"10x{current_height}+{screen_width-10}+{int((screen_height-current_height)/2)}")
            
        # Bind hover to restore
        self.root.bind("<Enter>", self._restore_from_collapse)
        
    def _restore_from_collapse(self, event=None) -> None:
        """Restore window from collapsed state"""
        if hasattr(self.root, "collapse_restore"):
            width = self.root.collapse_restore["width"]
            height = self.root.collapse_restore["height"]
            x, y = self.root.collapse_restore["position"]
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            self.root.unbind("<Enter>")
            
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
            
            # Move to top if that setting is enabled
            if self.app.settings.get("general", "last_used_to_top", True):
                # Remove from current position
                self.app.clipboard_manager.history.remove(item)
                # Add to end (most recent)
                self.app.clipboard_manager.history.append(item)
                # Update the UI
                self._update_clipboard_list()
            
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
        context_menu = tk.Menu(self.root, tearoff=0, bg='#2C2C2C', fg='#FFFFFF', activebackground='#505050')
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
            label="Add as Note",
            command=self._add_selected_as_note
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
            
    def _add_selected_as_note(self) -> None:
        """Add selected clipboard item as a note"""
        selection = self.clip_list.curselection()
        if not selection:
            return
            
        index = selection[0]
        history_index = len(self.app.clipboard_manager.history) - 1 - index
        
        if 0 <= history_index < len(self.app.clipboard_manager.history):
            item = self.app.clipboard_manager.history[history_index]
            if item.content_type == 'text':
                # Truncate if too long for display
                display_text = item.content.split('\n')[0]
                if len(display_text) > 50:
                    display_text = display_text[:47] + "..."
                    
                # Add to notes list
                self.notes_list.insert(tk.END, display_text)
                self._save_notes()
                self.status_var.set("Added as note")
            
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
        # Create a new process
        import subprocess
        import sys
        
        try:
            subprocess.Popen([sys.executable, "main.py", "--new-window"])
            self.status_var.set("New window opened")
        except Exception as e:
            logger.error(f"Error opening new window: {str(e)}")
            self.status_var.set("Error opening new window")
        
    def _open_settings(self) -> None:
        """Open settings dialog"""
        # Create settings dialog
        settings_dialog = tk.Toplevel(self.root)
        settings_dialog.title("Settings")
        settings_dialog.geometry("600x500")
        settings_dialog.transient(self.root)
        settings_dialog.grab_set()
        
        # Configure dialog for dark theme
        settings_dialog.configure(bg='#2C2C2C')
        
        # Create notebook for tabs
        notebook = ttk.Notebook(settings_dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General settings tab
        general_frame = ttk.Frame(notebook, style="Modern.TFrame")
        notebook.add(general_frame, text="General")
        
        # UI settings tab
        ui_frame = ttk.Frame(notebook, style="Modern.TFrame")
        notebook.add(ui_frame, text="UI")
        
        # Hotkeys tab
        hotkeys_frame = ttk.Frame(notebook, style="Modern.TFrame")
        notebook.add(hotkeys_frame, text="Hotkeys")
        
        # Plugins tab
        plugins_frame = ttk.Frame(notebook, style="Modern.TFrame")
        notebook.add(plugins_frame, text="Plugins")
        
        # Security tab
        security_frame = ttk.Frame(notebook, style="Modern.TFrame")
        notebook.add(security_frame, text="Security")
        
        # Add settings controls to each tab
        self._create_general_settings(general_frame)
        self._create_ui_settings(ui_frame)
        self._create_hotkeys_settings(hotkeys_frame)
        self._create_plugins_settings(plugins_frame)
        self._create_security_settings(security_frame)
        
        # Buttons frame
        btn_frame = ttk.Frame(settings_dialog, style="Modern.TFrame")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Save button
        save_btn = ttk.Button(
            btn_frame,
            text="Save",
            style="Modern.TButton",
            command=lambda: self._save_settings(settings_dialog)
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(
            btn_frame,
            text="Cancel",
            style="Modern.TButton",
            command=settings_dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Reset button
        reset_btn = ttk.Button(
            btn_frame,
            text="Reset to Defaults",
            style="Modern.TButton",
            command=lambda: self._reset_settings(settings_dialog)
        )
        reset_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_general_settings(self, parent):
        """Create general settings controls"""
        # Max history items setting
        max_history_frame = ttk.Frame(parent, style="Modern.TFrame")
        max_history_frame.pack(fill=tk.X, padx=10, pady=5)
        
        max_history_label = ttk.Label(
            max_history_frame,
            text="Maximum clipboard history items:",
            style="Modern.TLabel"
        )
        max_history_label.pack(side=tk.LEFT, padx=5)
        
        max_history_var = tk.IntVar(value=self.app.settings.get("general", "max_history_items", 100))
        max_history_entry = ttk.Spinbox(
            max_history_frame,
            from_=10,
            to=1000,
            increment=10,
            textvariable=max_history_var,
            width=5,
            style="Modern.TSpinbox"
        )
        max_history_entry.pack(side=tk.LEFT, padx=5)
        
        # Poll interval setting
        poll_frame = ttk.Frame(parent, style="Modern.TFrame")
        poll_frame.pack(fill=tk.X, padx=10, pady=5)
        
        poll_label = ttk.Label(
            poll_frame,
            text="Clipboard poll interval (seconds):",
            style="Modern.TLabel"
        )
        poll_label.pack(side=tk.LEFT, padx=5)
        
        poll_var = tk.DoubleVar(value=self.app.settings.get("general", "clipboard_poll_interval", 0.5))
        poll_entry = ttk.Spinbox(
            poll_frame,
            from_=0.1,
            to=5.0,
            increment=0.1,
            textvariable=poll_var,
            width=5,
            style="Modern.TSpinbox"
        )
        poll_entry.pack(side=tk.LEFT, padx=5)
        
        # Startup settings
        startup_frame = ttk.LabelFrame(parent, text="Startup", style="Modern.TLabelframe")
        startup_frame.pack(fill=tk.X, padx=10, pady=10)
        
        start_minimized_var = tk.BooleanVar(value=self.app.settings.get("general", "start_minimized", False))
        start_minimized_cb = ttk.Checkbutton(
            startup_frame,
            text="Start minimized",
            variable=start_minimized_var,
            style="Modern.TCheckbutton"
        )
        start_minimized_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        start_with_system_var = tk.BooleanVar(value=self.app.settings.get("general", "start_with_system", False))
        start_with_system_cb = ttk.Checkbutton(
            startup_frame,
            text="Start with system",
            variable=start_with_system_var,
            style="Modern.TCheckbutton"
        )
        start_with_system_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Behavior settings
        behavior_frame = ttk.LabelFrame(parent, text="Behavior", style="Modern.TLabelframe")
        behavior_frame.pack(fill=tk.X, padx=10, pady=10)
        
        confirm_delete_var = tk.BooleanVar(value=self.app.settings.get("general", "confirm_delete", True))
        confirm_delete_cb = ttk.Checkbutton(
            behavior_frame,
            text="Confirm before deleting items",
            variable=confirm_delete_var,
            style="Modern.TCheckbutton"
        )
        confirm_delete_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        hide_after_paste_var = tk.BooleanVar(value=self.app.settings.get("general", "hide_after_paste", True))
        hide_after_paste_cb = ttk.Checkbutton(
            behavior_frame,
            text="Hide after pasting an item",
            variable=hide_after_paste_var,
            style="Modern.TCheckbutton"
        )
        hide_after_paste_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        minimize_to_tray_var = tk.BooleanVar(value=self.app.settings.get("general", "minimize_to_tray_on_close", True))
        minimize_to_tray_cb = ttk.Checkbutton(
            behavior_frame,
            text="Minimize to tray when closing",
            variable=minimize_to_tray_var,
            style="Modern.TCheckbutton"
        )
        minimize_to_tray_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        last_used_to_top_var = tk.BooleanVar(value=self.app.settings.get("general", "last_used_to_top", True))
        last_used_to_top_cb = ttk.Checkbutton(
            behavior_frame,
            text="Move last used item to top",
            variable=last_used_to_top_var,
            style="Modern.TCheckbutton"
        )
        last_used_to_top_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Store variables for later retrieval
        parent.settings_vars = {
            "max_history_items": max_history_var,
            "clipboard_poll_interval": poll_var,
            "start_minimized": start_minimized_var,
            "start_with_system": start_with_system_var,
            "confirm_delete": confirm_delete_var,
            "hide_after_paste": hide_after_paste_var,
            "minimize_to_tray_on_close": minimize_to_tray_var,
            "last_used_to_top": last_used_to_top_var
        }
    
    def _create_ui_settings(self, parent):
        """Create UI settings controls"""
        # Theme settings
        theme_frame = ttk.LabelFrame(parent, text="Theme", style="Modern.TLabelframe")
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        theme_label = ttk.Label(
            theme_frame,
            text="Theme:",
            style="Modern.TLabel"
        )
        theme_label.pack(side=tk.LEFT, padx=5)
        
        theme_var = tk.StringVar(value=self.app.settings.get("ui", "theme", "system"))
        themes = [("Light", "light"), ("Dark", "dark"), ("System", "system"), ("High Contrast", "high_contrast")]
        
        theme_frame_rb = ttk.Frame(theme_frame, style="Modern.TFrame")
        theme_frame_rb.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        for text, value in themes:
            rb = ttk.Radiobutton(
                theme_frame_rb,
                text=text,
                value=value,
                variable=theme_var,
                style="Modern.TRadiobutton"
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Font size settings
        font_frame = ttk.Frame(parent, style="Modern.TFrame")
        font_frame.pack(fill=tk.X, padx=10, pady=10)
        
        font_label = ttk.Label(
            font_frame,
            text="Font size:",
            style="Modern.TLabel"
        )
        font_label.pack(side=tk.LEFT, padx=5)
        
        font_var = tk.IntVar(value=self.app.settings.get("ui", "font_size", 12))
        font_entry = ttk.Spinbox(
            font_frame,
            from_=8,
            to=24,
            increment=1,
            textvariable=font_var,
            width=5,
            style="Modern.TSpinbox"
        )
        font_entry.pack(side=tk.LEFT, padx=5)
        
        # Display options
        display_frame = ttk.LabelFrame(parent, text="Display Options", style="Modern.TLabelframe")
        display_frame.pack(fill=tk.X, padx=10, pady=10)
        
        always_on_top_var = tk.BooleanVar(value=self.app.settings.get("ui", "always_on_top", False))
        always_on_top_cb = ttk.Checkbutton(
            display_frame,
            text="Always on top",
            variable=always_on_top_var,
            style="Modern.TCheckbutton"
        )
        always_on_top_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        show_timestamps_var = tk.BooleanVar(value=self.app.settings.get("ui", "show_timestamps", True))
        show_timestamps_cb = ttk.Checkbutton(
            display_frame,
            text="Show timestamps",
            variable=show_timestamps_var,
            style="Modern.TCheckbutton"
        )
        show_timestamps_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Opacity settings
        opacity_frame = ttk.Frame(display_frame, style="Modern.TFrame")
        opacity_frame.pack(fill=tk.X, padx=10, pady=5)
        
        opacity_label = ttk.Label(
            opacity_frame,
            text="Window opacity:",
            style="Modern.TLabel"
        )
        opacity_label.pack(side=tk.LEFT, padx=5)
        
        opacity_var = tk.DoubleVar(value=self.app.settings.get("ui", "opacity", 1.0))
        opacity_scale = ttk.Scale(
            opacity_frame,
            from_=0.2,
            to=1.0,
            variable=opacity_var,
            orient=tk.HORIZONTAL,
            style="Modern.Horizontal.TScale"
        )
        opacity_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Auto-collapse settings
        collapse_frame = ttk.LabelFrame(parent, text="Auto-Collapse", style="Modern.TLabelframe")
        collapse_frame.pack(fill=tk.X, padx=10, pady=10)
        
        enable_collapse_var = tk.BooleanVar(value=self.app.settings.get("ui", "enable_auto_collapse", False))
        enable_collapse_cb = ttk.Checkbutton(
            collapse_frame,
            text="Enable auto-collapse",
            variable=enable_collapse_var,
            style="Modern.TCheckbutton"
        )
        enable_collapse_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Store variables for later retrieval
        parent.settings_vars = {
            "theme": theme_var,
            "font_size": font_var,
            "always_on_top": always_on_top_var,
            "show_timestamps": show_timestamps_var,
            "opacity": opacity_var,
            "enable_auto_collapse": enable_collapse_var
        }
    
    def _create_hotkeys_settings(self, parent):
        """Create hotkey settings controls"""
        hotkeys = [
            ("Toggle visibility", "toggle_visibility", "ctrl+shift+c"),
            ("Paste last item", "paste_last_item", "ctrl+shift+v"),
            ("Clear history", "clear_history", "ctrl+shift+x")
        ]
        
        hotkey_vars = {}
        
        for i, (label_text, key, default) in enumerate(hotkeys):
            frame = ttk.Frame(parent, style="Modern.TFrame")
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            label = ttk.Label(
                frame,
                text=f"{label_text}:",
                width=20,
                anchor=tk.W,
                style="Modern.TLabel"
            )
            label.pack(side=tk.LEFT, padx=5)
            
            current_hotkey = self.app.settings.get("hotkeys", key, default)
            var = tk.StringVar(value=current_hotkey)
            entry = ttk.Entry(
                frame,
                textvariable=var,
                width=20,
                style="Modern.TEntry"
            )
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            record_btn = ttk.Button(
                frame,
                text="Record",
                style="Modern.TButton",
                command=lambda e=entry, v=var: self._record_hotkey(e, v)
            )
            record_btn.pack(side=tk.LEFT, padx=5)
            
            reset_btn = ttk.Button(
                frame,
                text="Reset",
                style="Modern.TButton",
                command=lambda v=var, d=default: v.set(d)
            )
            reset_btn.pack(side=tk.LEFT, padx=5)
            
            hotkey_vars[key] = var
        
        # Store variables for later retrieval
        parent.settings_vars = hotkey_vars
    
    def _record_hotkey(self, entry, var):
        """Record a new hotkey"""
        # Disable the entry and change its text
        entry.config(state=tk.DISABLED)
        old_value = var.get()
        var.set("Press key combination...")
        
        # Create a recording window
        record_win = tk.Toplevel(self.root)
        record_win.title("Record Hotkey")
        record_win.geometry("300x100")
        record_win.transient(self.root)
        record_win.grab_set()
        
        # Configure for dark theme
        record_win.configure(bg='#2C2C2C')
        
        # Add instructions
        label = ttk.Label(
            record_win,
            text="Press the key combination you want to use\nor Escape to cancel.",
            style="Modern.TLabel"
        )
        label.pack(pady=20)
        
        # Function to handle key press
        def on_key(event):
            keys = []
            if event.keysym == "Escape":
                # Cancel recording
                var.set(old_value)
                record_win.destroy()
                entry.config(state=tk.NORMAL)
                return
                
            # Check for modifiers
            if event.state & 0x4:  # Control
                keys.append("ctrl")
            if event.state & 0x1:  # Shift
                keys.append("shift")
            if event.state & 0x8:  # Alt
                keys.append("alt")
                
            # Add the key itself
            if event.keysym not in ("Control_L", "Control_R", "Shift_L", "Shift_R", "Alt_L", "Alt_R"):
                keys.append(event.keysym.lower())
                
            # Set the hotkey
            if keys:
                hotkey = "+".join(keys)
                var.set(hotkey)
                record_win.destroy()
                entry.config(state=tk.NORMAL)
        
        # Bind key events
        record_win.bind("<Key>", on_key)
    
    def _create_plugins_settings(self, parent):
        """Create plugin settings controls"""
        # Plugin manager frame
        self.plugin_manager_frame = ttk.Frame(parent, style="Modern.TFrame")
        self.plugin_manager_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Plugin list
        list_frame = ttk.LabelFrame(self.plugin_manager_frame, text="Available Plugins", style="Modern.TLabelframe")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a listbox with scrollbar for plugins
        self.plugin_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            font=('Segoe UI', 10),
            bg='#2C2C2C',  # Dark background
            fg='#FFFFFF',  # White text
            highlightbackground='#3C3C3C',
            highlightcolor='#3C3C3C',
            selectbackground='#505050',
            selectforeground='#FFFFFF',
        )
        self.plugin_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        
        plugin_scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.plugin_listbox.yview
        )
        plugin_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.plugin_listbox.config(yscrollcommand=plugin_scrollbar.set)
        
        # Plugin details frame
        details_frame = ttk.LabelFrame(self.plugin_manager_frame, text="Plugin Details", style="Modern.TLabelframe")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Plugin name
        plugin_name_var = tk.StringVar()
        plugin_name_label = ttk.Label(
            details_frame,
            textvariable=plugin_name_var,
            style="Modern.Title.TLabel"
        )
        plugin_name_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Plugin description
        plugin_desc_var = tk.StringVar()
        plugin_desc_label = ttk.Label(
            details_frame,
            textvariable=plugin_desc_var,
            style="Modern.TLabel"
        )
        plugin_desc_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Plugin version and author
        plugin_meta_var = tk.StringVar()
        plugin_meta_label = ttk.Label(
            details_frame,
            textvariable=plugin_meta_var,
            style="Modern.TLabel"
        )
        plugin_meta_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Plugin enabled status
        plugin_enabled_var = tk.BooleanVar(value=False)
        plugin_enabled_cb = ttk.Checkbutton(
            details_frame,
            text="Enabled",
            variable=plugin_enabled_var,
            style="Modern.TCheckbutton"
        )
        plugin_enabled_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(parent, style="Modern.TFrame")
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Refresh button
        refresh_btn = ttk.Button(
            btn_frame,
            text="Refresh List",
            style="Modern.TButton",
            command=lambda: self._refresh_plugin_list()
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Store variables for later retrieval
        parent.settings_vars = {
            "plugin_enabled": plugin_enabled_var,
            "plugin_name": plugin_name_var,
            "plugin_desc": plugin_desc_var,
            "plugin_meta": plugin_meta_var
        }
        
        # Load the plugin list
        self._refresh_plugin_list()
        
        # Bind selection event
        self.plugin_listbox.bind("<<ListboxSelect>>", lambda e: self._on_plugin_selected(
            plugin_name_var, plugin_desc_var, plugin_meta_var, plugin_enabled_var
        ))
    
    def _refresh_plugin_list(self):
        """Refresh the list of available plugins"""
        self.plugin_listbox.delete(0, tk.END)
        
        # Get all plugins
        plugins = self.app.plugin_manager.discover_plugins()
        enabled_plugins = self.app.settings.get("plugins", "enabled", [])
        
        # Add to the list
        for plugin_name in plugins:
            # Load the plugin if not already loaded
            plugin = self.app.plugin_manager.plugins.get(plugin_name)
            if not plugin:
                plugin = self.app.plugin_manager.load_plugin(plugin_name)
                
            if plugin:
                # Mark enabled plugins with an asterisk
                prefix = "* " if plugin_name in enabled_plugins else "  "
                self.plugin_listbox.insert(tk.END, f"{prefix}{plugin.name}")
                
        # Select first item if available
        if self.plugin_listbox.size() > 0:
            self.plugin_listbox.selection_set(0)
            self.plugin_listbox.event_generate("<<ListboxSelect>>")
    
    def _on_plugin_selected(self, name_var, desc_var, meta_var, enabled_var):
        """Handle plugin selection"""
        selection = self.plugin_listbox.curselection()
        if not selection:
            return
            
        # Get the plugin name from the listbox
        display_name = self.plugin_listbox.get(selection[0])
        if display_name.startswith("* "):
            display_name = display_name[2:]
            
        # Find the plugin module name
        module_name = None
        for plugin_name, plugin in self.app.plugin_manager.plugins.items():
            if plugin.name == display_name:
                module_name = plugin_name
                break
                
        if not module_name:
            return
            
        # Get the plugin
        plugin = self.app.plugin_manager.plugins.get(module_name)
        if not plugin:
            return
            
        # Update the UI
        name_var.set(plugin.name)
        desc_var.set(plugin.description)
        meta_var.set(f"Version {plugin.version} by {plugin.author}")
        
        # Check if plugin is enabled
        enabled_plugins = self.app.settings.get("plugins", "enabled", [])
        enabled_var.set(module_name in enabled_plugins)
        
        # Update the enabled checkbox command
        enabled_cb = next((w for w in self.plugin_manager_frame.winfo_children()
                          if isinstance(w, ttk.Checkbutton) and str(w.cget("variable")).endswith("plugin_enabled")),
                         None)
        if enabled_cb:
            enabled_cb.config(command=lambda p=module_name, v=enabled_var: self._toggle_plugin(p, v))
    
    def _toggle_plugin(self, plugin_name, enabled_var):
        """Toggle plugin enabled state"""
        is_enabled = enabled_var.get()
        enabled_plugins = self.app.settings.get("plugins", "enabled", [])
        
        if is_enabled and plugin_name not in enabled_plugins:
            # Enable the plugin
            success = self.app.plugin_manager.enable_plugin(plugin_name)
            if success:
                enabled_plugins.append(plugin_name)
                self.app.settings.set("plugins", "enabled", enabled_plugins)
                self._refresh_plugin_list()
            else:
                # Revert the checkbox if enabling failed
                enabled_var.set(False)
                messagebox.showerror("Error", f"Failed to enable plugin '{plugin_name}'", parent=self.root)
        elif not is_enabled and plugin_name in enabled_plugins:
            # Disable the plugin
            success = self.app.plugin_manager.disable_plugin(plugin_name)
            if success:
                enabled_plugins.remove(plugin_name)
                self.app.settings.set("plugins", "enabled", enabled_plugins)
                self._refresh_plugin_list()
            else:
                # Revert the checkbox if disabling failed
                enabled_var.set(True)
                messagebox.showerror("Error", f"Failed to disable plugin '{plugin_name}'", parent=self.root)
    
    def _create_security_settings(self, parent):
        """Create security settings controls"""
        # Security settings frame
        security_frame = ttk.LabelFrame(parent, text="Security Options", style="Modern.TLabelframe")
        security_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Encrypt sensitive content
        encrypt_var = tk.BooleanVar(value=self.app.settings.get("security", "encrypt_sensitive", False))
        encrypt_cb = ttk.Checkbutton(
            security_frame,
            text="Encrypt sensitive content",
            variable=encrypt_var,
            style="Modern.TCheckbutton"
        )
        encrypt_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Auto-clear passwords
        auto_clear_var = tk.BooleanVar(value=self.app.settings.get("security", "auto_clear_passwords", True))
        auto_clear_cb = ttk.Checkbutton(
            security_frame,
            text="Auto-clear passwords after 1 minute",
            variable=auto_clear_var,
            style="Modern.TCheckbutton"
        )
        auto_clear_cb.pack(anchor=tk.W, padx=10, pady=5)
        
        # Encryption key settings
        if self.app.settings.get("security", "encrypt_sensitive", False):
            key_frame = ttk.Frame(parent, style="Modern.TFrame")
            key_frame.pack(fill=tk.X, padx=10, pady=10)
            
            key_label = ttk.Label(
                key_frame,
                text="Encryption key:",
                style="Modern.TLabel"
            )
            key_label.pack(side=tk.LEFT, padx=5)
            
            key_var = tk.StringVar(value=self.app.settings.get("security", "encrypt_key", ""))
            key_entry = ttk.Entry(
                key_frame,
                textvariable=key_var,
                show="•",
                width=30,
                style="Modern.TEntry"
            )
            key_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Change key button
            change_key_btn = ttk.Button(
                key_frame,
                text="Change Key",
                style="Modern.TButton",
                command=lambda: self._change_encryption_key(key_var)
            )
            change_key_btn.pack(side=tk.LEFT, padx=5)
        
        # Store variables for later retrieval
        security_vars = {
            "encrypt_sensitive": encrypt_var,
            "auto_clear_passwords": auto_clear_var
        }
        
        # Add encryption key if available
        if self.app.settings.get("security", "encrypt_sensitive", False):
            security_vars["encrypt_key"] = key_var
            
        parent.settings_vars = security_vars
    
    def _change_encryption_key(self, key_var):
        """Change the encryption key"""
        # This is just a placeholder, in a real app you'd re-encrypt existing data
        messagebox.showinfo("Encryption Key", "Key updated. This would re-encrypt all sensitive data with the new key.")
    
    def _save_settings(self, dialog):
        """Save settings from dialog"""
        # Get all tabs in the notebook
        notebook = next((w for w in dialog.winfo_children() if isinstance(w, ttk.Notebook)), None)
        if not notebook:
            return
        
        # Process each tab
        for tab_id in notebook.tabs():
            tab = notebook.nametowidget(tab_id)
            if not hasattr(tab, "settings_vars"):
                continue
                
            # Get the tab name
            tab_name = notebook.tab(tab_id, "text").lower()
            
            # Save settings from this tab
            for setting, var in tab.settings_vars.items():
                value = var.get()
                
                # Map tab names to settings sections
                section = {
                    "general": "general",
                    "ui": "ui",
                    "hotkeys": "hotkeys",
                    "security": "security"
                }.get(tab_name, tab_name)
                
                # Save the setting
                self.app.settings.set(section, setting, value)
        
        # Save plugin settings separately
        enabled_plugins = []
        for plugin_name, plugin in self.app.plugin_manager.plugins.items():
            if plugin.enabled:
                enabled_plugins.append(plugin_name)
        self.app.settings.set("plugins", "enabled", enabled_plugins)
        
        # Save settings to file
        self.app.settings.save()
        
        # Apply certain settings immediately
        self._apply_immediate_settings()
        
        # Close dialog
        dialog.destroy()
        
        # Show confirmation
        self.status_var.set("Settings saved")
    
    def _apply_immediate_settings(self):
        """Apply settings that need to take effect immediately"""
        # Apply theme
        theme = self.app.settings.get("ui", "theme", "system")
        self.app.theme_manager.apply_theme(theme)
        
        # Apply opacity
        opacity = self.app.settings.get("ui", "opacity", 1.0)
        self.root.attributes("-alpha", opacity)
        
        # Apply always on top
        always_on_top = self.app.settings.get("ui", "always_on_top", False)
        self.root.attributes("-topmost", always_on_top)
        self.always_on_top_var.set(always_on_top)
        
        # Apply font size
        font_size = self.app.settings.get("ui", "font_size", 12)
        self.clip_list.config(font=('Segoe UI', font_size))
        self.notes_list.config(font=('Segoe UI', font_size))
        
        # Restart clipboard monitoring with new poll interval
        poll_interval = self.app.settings.get("general", "clipboard_poll_interval", 0.5)
        self.app.clipboard_manager.stop_monitoring()
        self.app.clipboard_manager.start_monitoring(interval=poll_interval)
    
    def _reset_settings(self, dialog):
        """Reset settings to defaults"""
        confirm = messagebox.askyesno(
            "Confirm Reset",
            "Reset all settings to defaults?",
            parent=dialog
        )
        
        if confirm:
            self.app.settings.reset_to_defaults()
            dialog.destroy()
            messagebox.showinfo(
                "Settings Reset",
                "All settings have been reset to their default values.\n\n"
                "Please restart the application for all changes to take effect.",
                parent=self.root
            )
    
    def _open_plugins(self) -> None:
        """Open plugins manager"""
        # This just opens the plugins tab in the settings dialog
        self._open_settings()
        
    def _open_docs(self) -> None:
        """Open documentation"""
        messagebox.showinfo(
            "Documentation",
            "Documentation would open in your default browser.",
            parent=self.root
        )
        
    def _show_about(self) -> None:
        """Show about dialog"""
        # Show a simple about message box
        tk.messagebox.showinfo(
            "About ClipScribe Plus",
            "ClipScribe Plus - Advanced Clipboard Manager\n"
            "Version 1.0.0\n\n"
            "A powerful clipboard manager with plugin support,\n"
            "custom themes, and advanced features.",
            parent=self.root
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
        
        # Make sure dialog follows dark theme
        dialog.configure(bg='#2C2C2C')
        
        # Current opacity
        current_opacity = self.app.settings.get("ui", "opacity", 1.0)
        
        # Label
        ttk.Label(dialog, text="Window Opacity:", style="Modern.TLabel").pack(pady=5)
        
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
            command=update_opacity,
            style="Modern.Horizontal.TScale"
        )
        slider.pack(fill=tk.X, padx=20, pady=5)
        
        # Button frame
        btn_frame = ttk.Frame(dialog, style="Modern.TFrame")
        btn_frame.pack(fill=tk.X, pady=10)
        
        # OK button
        def ok_clicked():
            value = opacity_var.get()
            self.app.settings.set("ui", "opacity", value)
            self.app.settings.save()
            dialog.destroy()
            
        ttk.Button(btn_frame, text="OK", style="Modern.TButton", command=ok_clicked).pack(side=tk.RIGHT, padx=5)
        
        # Cancel button
        def cancel_clicked():
            self.root.attributes("-alpha", current_opacity)
            dialog.destroy()
            
        ttk.Button(btn_frame, text="Cancel", style="Modern.TButton", command=cancel_clicked).pack(side=tk.RIGHT, padx=5)
        
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
        
        # Load notes
        self._load_notes()
        
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

