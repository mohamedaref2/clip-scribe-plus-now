
"""
Clipboard manager module for handling clipboard operations.
Monitors and manages clipboard content across the system.
"""
import logging
import time
import threading
from typing import Callable, Dict, List, Optional, Any, Union
import tkinter as tk
from PIL import Image, ImageTk
import io

logger = logging.getLogger(__name__)

class ClipboardItem:
    """Represents a single clipboard item that can be text, image, or other data"""
    
    def __init__(self, content: Any, content_type: str, timestamp: float = None):
        """
        Initialize a clipboard item
        
        Args:
            content: The actual content (text string, image data, etc.)
            content_type: Type of the content ('text', 'image', etc.)
            timestamp: When this item was created/copied
        """
        self.content = content
        self.content_type = content_type
        self.timestamp = timestamp or time.time()
        self.tags: List[str] = []
        self.favorite = False
        
    def __str__(self) -> str:
        """String representation of the clipboard item"""
        if self.content_type == 'text':
            preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
            return f"Text: {preview}"
        elif self.content_type == 'image':
            return f"Image: {self.content.width}x{self.content.height}"
        else:
            return f"Item: {self.content_type}"


class ClipboardManager:
    """
    Manages clipboard operations, monitoring, and history.
    Provides methods to interact with the system clipboard.
    """
    
    def __init__(self, max_history: int = 100):
        """
        Initialize the clipboard manager
        
        Args:
            max_history: Maximum number of items to keep in history
        """
        self.max_history = max_history
        self.history: List[ClipboardItem] = []
        self.current_index = -1
        self.clipboard = tk.Tk()
        self.clipboard.withdraw()  # Hide the window
        self.monitor_thread = None
        self.stop_monitoring = threading.Event()
        self.on_clipboard_change_callbacks: List[Callable[[ClipboardItem], None]] = []
        
        # For undo/redo functionality
        self.undo_stack: List[ClipboardItem] = []
        self.redo_stack: List[ClipboardItem] = []
        
        logger.debug("ClipboardManager initialized")
        
    def start_monitoring(self, interval: float = 0.5) -> None:
        """
        Start monitoring the clipboard for changes
        
        Args:
            interval: How often to check for changes (in seconds)
        """
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            logger.warning("Clipboard monitoring already active")
            return
            
        self.stop_monitoring.clear()
        self.monitor_thread = threading.Thread(
            target=self._monitor_clipboard,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Clipboard monitoring started")
        
    def stop_monitoring(self) -> None:
        """Stop monitoring the clipboard"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            logger.warning("Clipboard monitoring not active")
            return
            
        self.stop_monitoring.set()
        self.monitor_thread.join(timeout=2.0)
        logger.info("Clipboard monitoring stopped")
        
    def _monitor_clipboard(self, interval: float) -> None:
        """
        Monitor the clipboard for changes
        
        Args:
            interval: How often to check for changes (in seconds)
        """
        last_content = None
        
        try:
            while not self.stop_monitoring.is_set():
                try:
                    # Try to get text content
                    current_content = self.clipboard.clipboard_get()
                    content_type = 'text'
                except tk.TclError:
                    try:
                        # Try to get image content
                        current_content = ImageTk.PhotoImage(self.clipboard.clipboard_get(type='image'))
                        content_type = 'image'
                    except (tk.TclError, Exception):
                        current_content = None
                        content_type = None
                
                # If we got content and it's different from the last one
                if (current_content is not None and 
                    (last_content is None or 
                     (content_type == 'text' and current_content != last_content) or 
                     (content_type == 'image'))):
                    
                    clip_item = ClipboardItem(current_content, content_type)
                    self._add_to_history(clip_item)
                    
                    # Notify callbacks
                    for callback in self.on_clipboard_change_callbacks:
                        try:
                            callback(clip_item)
                        except Exception as e:
                            logger.error(f"Error in clipboard change callback: {e}")
                    
                    last_content = current_content if content_type == 'text' else None
                
                # Wait before checking again
                time.sleep(interval)
                
        except Exception as e:
            logger.error(f"Error in clipboard monitoring thread: {e}")
            
    def _add_to_history(self, item: ClipboardItem) -> None:
        """
        Add an item to clipboard history
        
        Args:
            item: The clipboard item to add
        """
        # Clear redo stack when new item is added
        self.redo_stack.clear()
        
        # Add to history and maintain max size
        self.history.append(item)
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        # Update current index
        self.current_index = len(self.history) - 1
        
    def copy_to_clipboard(self, item: ClipboardItem) -> None:
        """
        Copy an item to the system clipboard
        
        Args:
            item: The clipboard item to copy
        """
        if item.content_type == 'text':
            self.clipboard.clipboard_clear()
            self.clipboard.clipboard_append(item.content)
        elif item.content_type == 'image':
            self.clipboard.clipboard_clear()
            self.clipboard.clipboard_append(item.content)
        
        # Add to undo stack
        self.undo_stack.append(item)
        
    def undo(self) -> Optional[ClipboardItem]:
        """
        Undo the last clipboard operation
        
        Returns:
            The previous clipboard item, or None if there's nothing to undo
        """
        if not self.undo_stack:
            return None
            
        item = self.undo_stack.pop()
        self.redo_stack.append(item)
        
        if self.undo_stack:
            prev_item = self.undo_stack[-1]
            self.copy_to_clipboard(prev_item)
            return prev_item
        return None
        
    def redo(self) -> Optional[ClipboardItem]:
        """
        Redo a previously undone clipboard operation
        
        Returns:
            The redone clipboard item, or None if there's nothing to redo
        """
        if not self.redo_stack:
            return None
            
        item = self.redo_stack.pop()
        self.undo_stack.append(item)
        self.copy_to_clipboard(item)
        return item
        
    def add_clipboard_change_listener(self, callback: Callable[[ClipboardItem], None]) -> None:
        """
        Add a callback to be notified on clipboard changes
        
        Args:
            callback: The function to call when clipboard changes
        """
        if callback not in self.on_clipboard_change_callbacks:
            self.on_clipboard_change_callbacks.append(callback)
            
    def remove_clipboard_change_listener(self, callback: Callable[[ClipboardItem], None]) -> None:
        """
        Remove a previously added clipboard change listener
        
        Args:
            callback: The callback function to remove
        """
        if callback in self.on_clipboard_change_callbacks:
            self.on_clipboard_change_callbacks.remove(callback)
