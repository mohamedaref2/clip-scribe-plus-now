
#!/usr/bin/env python3
"""
ClipScribe Plus - Advanced Clipboard Manager
Main entry point for the application
"""
import logging
import os
import sys
import tkinter as tk
from tkinter import messagebox

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("clipscribe.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure all required directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        "data", 
        "logs", 
        "plugins", 
        "themes", 
        "images/cache", 
        "config"
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
def main():
    """Main application entry point"""
    logger.info("Starting ClipScribe Plus Clipboard Manager")
    
    try:
        # Create the directories
        ensure_directories()
        
        # Import after directories are created to avoid issues
        from ui.app import ClipScribeApp
        
        # Create the root Tk instance
        root = tk.Tk()
        root.withdraw()  # Hide the root window initially
        
        # Initialize the application
        app = ClipScribeApp(root)
        
        # Start the main event loop
        root.mainloop()
        
    except Exception as e:
        logger.exception("Fatal error in main program")
        messagebox.showerror("Error", f"An error occurred: {str(e)}\n\nSee log file for details.")
        return 1
    
    logger.info("ClipScribe Plus shutting down normally")
    return 0

if __name__ == "__main__":
    sys.exit(main())
