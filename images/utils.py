
"""
Utilities for working with images in the clipboard manager.
"""
import logging
import os
import hashlib
from io import BytesIO
from typing import Optional, Tuple
import tkinter as tk

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available, image functionality will be limited")
    
logger = logging.getLogger(__name__)

class ImageManager:
    """
    Manages image operations for the clipboard manager.
    Handles caching, thumbnailing, and other image processing.
    """
    
    def __init__(self, cache_dir: str = "images/cache", max_cache_size: int = 100):
        """
        Initialize image manager
        
        Args:
            cache_dir: Directory to store cached images
            max_cache_size: Maximum number of images to keep in cache
        """
        self.cache_dir = cache_dir
        self.max_cache_size = max_cache_size
        self.cache = {}  # In-memory cache
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        logger.debug("ImageManager initialized")
        
    def image_to_thumbnail(self, 
                          image_data: bytes, 
                          size: Tuple[int, int] = (100, 100)) -> Optional[ImageTk.PhotoImage]:
        """
        Convert image data to a thumbnail
        
        Args:
            image_data: Raw image data bytes
            size: Thumbnail dimensions (width, height)
            
        Returns:
            Tkinter-compatible thumbnail image, or None if failed
        """
        if not PIL_AVAILABLE:
            logger.error("Cannot create thumbnail: PIL not available")
            return None
            
        try:
            # Create PIL image from data
            img = Image.open(BytesIO(image_data))
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert to Tkinter-compatible image
            return ImageTk.PhotoImage(img)
        except Exception as e:
            logger.error(f"Error creating thumbnail: {str(e)}")
            return None
            
    def cache_image(self, image_data: bytes, key: Optional[str] = None) -> str:
        """
        Cache an image for later use
        
        Args:
            image_data: Raw image data bytes
            key: Optional key to store the image under
            
        Returns:
            Cache key for the stored image
        """
        try:
            # Generate a key if not provided
            if key is None:
                key = hashlib.md5(image_data).hexdigest()
                
            # Store in memory cache
            self.cache[key] = image_data
            
            # Optionally, also save to disk
            cache_path = os.path.join(self.cache_dir, f"{key}.png")
            if not os.path.exists(cache_path):
                if PIL_AVAILABLE:
                    try:
                        img = Image.open(BytesIO(image_data))
                        img.save(cache_path)
                    except Exception as e:
                        logger.error(f"Error saving image to cache: {str(e)}")
                else:
                    # Fallback: just write the raw bytes
                    with open(cache_path, 'wb') as f:
                        f.write(image_data)
                        
            # Manage cache size
            self._manage_cache_size()
            
            return key
        except Exception as e:
            logger.error(f"Error caching image: {str(e)}")
            return ""
            
    def get_cached_image(self, key: str) -> Optional[bytes]:
        """
        Get an image from the cache
        
        Args:
            key: Cache key for the image
            
        Returns:
            Raw image data if found, None otherwise
        """
        # Check memory cache first
        if key in self.cache:
            return self.cache[key]
            
        # Try disk cache
        cache_path = os.path.join(self.cache_dir, f"{key}.png")
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    data = f.read()
                    
                # Update memory cache
                self.cache[key] = data
                return data
            except Exception as e:
                logger.error(f"Error reading image from cache: {str(e)}")
                
        return None
        
    def _manage_cache_size(self) -> None:
        """Manage cache size by removing old entries if needed"""
        if len(self.cache) <= self.max_cache_size:
            return
            
        # Remove oldest items from memory cache
        excess = len(self.cache) - self.max_cache_size
        keys_to_remove = list(self.cache.keys())[:excess]
        
        for key in keys_to_remove:
            del self.cache[key]
            
        logger.debug(f"Removed {excess} items from image cache")
        
    def clear_cache(self) -> None:
        """Clear all cached images"""
        self.cache.clear()
        
        # Clear disk cache
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.png'):
                    os.remove(os.path.join(self.cache_dir, file))
                    
            logger.info("Image cache cleared")
        except Exception as e:
            logger.error(f"Error clearing image cache: {str(e)}")
