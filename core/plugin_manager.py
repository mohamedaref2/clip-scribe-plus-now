
"""
Plugin manager for loading and managing ClipScribe plugins.
"""
import importlib.util
import inspect
import logging
import os
import sys
from typing import Dict, List, Optional, Type, Any, Callable

logger = logging.getLogger(__name__)

class Plugin:
    """Base class for all plugins"""
    
    # Plugin metadata
    name = "Base Plugin"
    description = "Base plugin class"
    version = "1.0.0"
    author = "Unknown"
    
    def __init__(self, app):
        """
        Initialize the plugin with the application instance
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.enabled = False
        
    def enable(self) -> bool:
        """
        Enable the plugin
        
        Returns:
            bool: True if successfully enabled, False otherwise
        """
        self.enabled = True
        return True
        
    def disable(self) -> bool:
        """
        Disable the plugin
        
        Returns:
            bool: True if successfully disabled, False otherwise
        """
        self.enabled = False
        return True
        
    def on_clipboard_change(self, item) -> None:
        """
        Called when clipboard content changes
        
        Args:
            item: The new clipboard item
        """
        pass
        
    def on_shutdown(self) -> None:
        """Called when the application is shutting down"""
        pass


class PluginManager:
    """
    Manages discovery, loading, and lifecycle of plugins.
    """
    
    def __init__(self, app, plugin_dir: str = "plugins"):
        """
        Initialize the plugin manager
        
        Args:
            app: The main application instance
            plugin_dir: Directory containing plugins
        """
        self.app = app
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Plugin] = {}
        self.enabled_plugins: Dict[str, Plugin] = {}
        
        # Ensure plugin directory exists
        os.makedirs(plugin_dir, exist_ok=True)
        
    def discover_plugins(self) -> List[str]:
        """
        Discover available plugins in the plugin directory
        
        Returns:
            List of plugin module names
        """
        discovered = []
        
        # Get all Python files in the plugin directory
        try:
            for file in os.listdir(self.plugin_dir):
                if file.endswith(".py") and not file.startswith("_"):
                    module_name = file[:-3]  # Remove .py extension
                    discovered.append(module_name)
                    
            logger.info(f"Discovered {len(discovered)} plugins: {', '.join(discovered)}")
            return discovered
        except Exception as e:
            logger.error(f"Error discovering plugins: {str(e)}")
            return []
            
    def load_plugin(self, module_name: str) -> Optional[Plugin]:
        """
        Load a plugin by module name
        
        Args:
            module_name: Name of the plugin module
            
        Returns:
            Plugin instance if loaded successfully, None otherwise
        """
        try:
            # Check if plugin is already loaded
            if module_name in self.plugins:
                logger.info(f"Plugin {module_name} already loaded")
                return self.plugins[module_name]
                
            # Build the full path to the plugin file
            plugin_path = os.path.join(self.plugin_dir, f"{module_name}.py")
            
            if not os.path.exists(plugin_path):
                logger.error(f"Plugin file not found: {plugin_path}")
                return None
                
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, plugin_path)
            if not spec or not spec.loader:
                logger.error(f"Failed to create module spec for {module_name}")
                return None
                
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Find the Plugin class in the module
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj is not Plugin):
                    plugin_class = obj
                    break
                    
            if not plugin_class:
                logger.error(f"No Plugin class found in {module_name}")
                return None
                
            # Create plugin instance
            plugin = plugin_class(self.app)
            self.plugins[module_name] = plugin
            
            logger.info(f"Loaded plugin: {plugin.name} v{plugin.version} by {plugin.author}")
            return plugin
            
        except Exception as e:
            logger.error(f"Failed to load plugin {module_name}: {str(e)}")
            return None
            
    def enable_plugin(self, module_name: str) -> bool:
        """
        Enable a plugin
        
        Args:
            module_name: Name of the plugin module
            
        Returns:
            bool: True if successfully enabled, False otherwise
        """
        # Load the plugin if not already loaded
        plugin = self.plugins.get(module_name)
        if not plugin:
            plugin = self.load_plugin(module_name)
            
        if not plugin:
            logger.error(f"Cannot enable plugin {module_name}: failed to load")
            return False
            
        # Enable the plugin
        try:
            success = plugin.enable()
            if success:
                self.enabled_plugins[module_name] = plugin
                logger.info(f"Enabled plugin: {plugin.name}")
            else:
                logger.warning(f"Plugin {plugin.name} refused to enable")
                
            return success
        except Exception as e:
            logger.error(f"Error enabling plugin {plugin.name}: {str(e)}")
            return False
            
    def disable_plugin(self, module_name: str) -> bool:
        """
        Disable a plugin
        
        Args:
            module_name: Name of the plugin module
            
        Returns:
            bool: True if successfully disabled, False otherwise
        """
        # Check if plugin is loaded and enabled
        plugin = self.plugins.get(module_name)
        
        if not plugin:
            logger.warning(f"Cannot disable plugin {module_name}: not loaded")
            return False
            
        if module_name not in self.enabled_plugins:
            logger.info(f"Plugin {plugin.name} is already disabled")
            return True
            
        # Disable the plugin
        try:
            success = plugin.disable()
            if success:
                del self.enabled_plugins[module_name]
                logger.info(f"Disabled plugin: {plugin.name}")
            else:
                logger.warning(f"Plugin {plugin.name} refused to disable")
                
            return success
        except Exception as e:
            logger.error(f"Error disabling plugin {plugin.name}: {str(e)}")
            return False
            
    def load_all_plugins(self) -> Dict[str, Optional[Plugin]]:
        """
        Discover and load all plugins
        
        Returns:
            Dictionary of module names and loaded plugin instances
        """
        modules = self.discover_plugins()
        result = {}
        
        for module_name in modules:
            plugin = self.load_plugin(module_name)
            result[module_name] = plugin
            
        return result
        
    def enable_all_plugins(self) -> Dict[str, bool]:
        """
        Enable all loaded plugins
        
        Returns:
            Dictionary of module names and enable results
        """
        result = {}
        
        for module_name in self.plugins:
            result[module_name] = self.enable_plugin(module_name)
            
        return result
        
    def get_plugin_by_name(self, name: str) -> Optional[Plugin]:
        """
        Find a plugin by its display name
        
        Args:
            name: Display name of the plugin
            
        Returns:
            Plugin instance if found, None otherwise
        """
        for plugin in self.plugins.values():
            if plugin.name == name:
                return plugin
        return None
        
    def notify_clipboard_change(self, item) -> None:
        """
        Notify all enabled plugins of a clipboard change
        
        Args:
            item: The clipboard item that changed
        """
        for plugin in self.enabled_plugins.values():
            try:
                plugin.on_clipboard_change(item)
            except Exception as e:
                logger.error(f"Error in plugin {plugin.name} on_clipboard_change: {str(e)}")
                
    def shutdown(self) -> None:
        """Clean shutdown of all enabled plugins"""
        for module_name, plugin in list(self.enabled_plugins.items()):
            try:
                plugin.on_shutdown()
                self.disable_plugin(module_name)
            except Exception as e:
                logger.error(f"Error shutting down plugin {plugin.name}: {str(e)}")
