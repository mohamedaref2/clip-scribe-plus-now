
"""
Global hotkeys management module.
Provides functionality to register and handle global keyboard shortcuts.
"""
import logging
import threading
from typing import Callable, Dict, Optional, Tuple

# We'll use pynput for cross-platform global hotkey handling
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logging.warning("pynput not available, hotkey functionality will be limited")
    
logger = logging.getLogger(__name__)

class HotkeyManager:
    """
    Manages global hotkeys for the application.
    Allows registering keyboard shortcuts that work application-wide.
    """
    
    def __init__(self):
        """Initialize hotkey manager"""
        self.hotkeys: Dict[str, Tuple[Callable, str]] = {}
        self.listener: Optional[keyboard.Listener] = None
        self.active = False
        self.current_keys = set()
        
    def start(self) -> bool:
        """
        Start listening for hotkeys
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if not PYNPUT_AVAILABLE:
            logger.error("Cannot start hotkey listener: pynput not available")
            return False
            
        if self.active:
            logger.warning("Hotkey listener already active")
            return True
            
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            self.active = True
            logger.info("Global hotkey listener started")
            return True
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {str(e)}")
            return False
            
    def stop(self) -> None:
        """Stop listening for hotkeys"""
        if self.listener and self.active:
            self.listener.stop()
            self.active = False
            logger.info("Global hotkey listener stopped")
            
    def _on_press(self, key) -> None:
        """
        Handle key press events
        
        Args:
            key: The key that was pressed
        """
        try:
            # Convert key to string representation
            key_str = self._key_to_string(key)
            if key_str:
                self.current_keys.add(key_str)
                
                # Check if current combination matches any hotkey
                current_combo = "+".join(sorted(self.current_keys))
                if current_combo in self.hotkeys:
                    callback, description = self.hotkeys[current_combo]
                    logger.debug(f"Hotkey triggered: {current_combo} ({description})")
                    
                    # Run callback in a separate thread to avoid blocking
                    threading.Thread(
                        target=self._run_callback,
                        args=(callback, current_combo),
                        daemon=True
                    ).start()
        except Exception as e:
            logger.error(f"Error handling key press: {str(e)}")
            
    def _on_release(self, key) -> None:
        """
        Handle key release events
        
        Args:
            key: The key that was released
        """
        try:
            key_str = self._key_to_string(key)
            if key_str and key_str in self.current_keys:
                self.current_keys.remove(key_str)
        except Exception as e:
            logger.error(f"Error handling key release: {str(e)}")
            
    def _key_to_string(self, key) -> Optional[str]:
        """
        Convert a pynput key to string representation
        
        Args:
            key: The key object from pynput
            
        Returns:
            String representation of the key, or None if conversion failed
        """
        if key is None:
            return None
            
        try:
            if isinstance(key, keyboard.Key):
                return key.name
            else:
                # For regular keys, get the character
                return key.char
        except Exception:
            return None
            
    def _run_callback(self, callback: Callable, hotkey: str) -> None:
        """
        Run a hotkey callback safely
        
        Args:
            callback: The function to call
            hotkey: The hotkey string that triggered this callback
        """
        try:
            callback()
        except Exception as e:
            logger.error(f"Error in hotkey callback for '{hotkey}': {str(e)}")
            
    def register_hotkey(self, 
                        keys: str, 
                        callback: Callable, 
                        description: str = "") -> bool:
        """
        Register a new global hotkey
        
        Args:
            keys: Key combination as string (e.g., 'ctrl+c', 'shift+alt+t')
            callback: Function to call when hotkey is triggered
            description: Human-readable description of what this hotkey does
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        if not PYNPUT_AVAILABLE:
            logger.error("Cannot register hotkey: pynput not available")
            return False
            
        # Normalize key combination
        key_combo = self._normalize_key_combo(keys)
        
        if key_combo in self.hotkeys:
            logger.warning(f"Hotkey {key_combo} already registered, overwriting")
            
        self.hotkeys[key_combo] = (callback, description)
        logger.info(f"Registered hotkey: {key_combo} ({description})")
        return True
        
    def unregister_hotkey(self, keys: str) -> bool:
        """
        Remove a previously registered hotkey
        
        Args:
            keys: Key combination to remove
            
        Returns:
            bool: True if unregistered successfully, False if not found
        """
        key_combo = self._normalize_key_combo(keys)
        
        if key_combo in self.hotkeys:
            del self.hotkeys[key_combo]
            logger.info(f"Unregistered hotkey: {key_combo}")
            return True
        else:
            logger.warning(f"Cannot unregister hotkey {key_combo}: not found")
            return False
            
    def _normalize_key_combo(self, keys: str) -> str:
        """
        Normalize a key combination string
        
        Args:
            keys: Input key combination (e.g., 'Ctrl+C', 'shift + alt + T')
            
        Returns:
            Normalized key combination (e.g., 'ctrl+c', 'alt+shift+t')
        """
        # Split by '+', strip whitespace, convert to lowercase, and sort
        parts = [part.strip().lower() for part in keys.split("+")]
        return "+".join(sorted(parts))
        
    def get_registered_hotkeys(self) -> Dict[str, str]:
        """
        Get all registered hotkeys and their descriptions
        
        Returns:
            Dictionary of hotkey combinations and descriptions
        """
        return {k: v[1] for k, v in self.hotkeys.items()}
