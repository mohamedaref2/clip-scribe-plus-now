
"""
Example plugin for text formatting in ClipScribe Plus.
"""
import logging
import re
from core.plugin_manager import Plugin

logger = logging.getLogger(__name__)

class TextFormatterPlugin(Plugin):
    """
    Plugin for formatting text in clipboard.
    Provides features like auto-capitalization, URL detection, etc.
    """
    
    # Plugin metadata
    name = "Text Formatter"
    description = "Formats and enhances text in the clipboard"
    version = "1.0.0"
    author = "ClipScribe Team"
    
    def __init__(self, app):
        super().__init__(app)
        self.auto_capitalize = True
        self.detect_urls = True
        self.clean_whitespace = True
        
    def enable(self) -> bool:
        """Enable the plugin"""
        logger.info("Enabling Text Formatter plugin")
        return super().enable()
        
    def disable(self) -> bool:
        """Disable the plugin"""
        logger.info("Disabling Text Formatter plugin")
        return super().disable()
        
    def on_clipboard_change(self, item) -> None:
        """
        Process text whenever clipboard changes
        
        Args:
            item: The new clipboard item
        """
        if not self.enabled:
            return
            
        if item.content_type != 'text':
            return  # Only process text items
            
        text = item.content
        
        # Apply formatting
        if self.clean_whitespace:
            text = self._clean_whitespace(text)
            
        if self.auto_capitalize:
            text = self._auto_capitalize(text)
            
        if self.detect_urls:
            text = self._detect_urls(text)
            
        # If text was modified, update the clipboard silently
        if text != item.content:
            logger.debug("Text formatter modified clipboard content")
            item.content = text
            
    def _clean_whitespace(self, text: str) -> str:
        """
        Clean extra whitespace from text
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Trim whitespace from beginning/end
        text = text.strip()
        
        # Remove extra newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
        
    def _auto_capitalize(self, text: str) -> str:
        """
        Auto-capitalize sentences
        
        Args:
            text: Input text
            
        Returns:
            Text with capitalized sentences
        """
        # Simple sentence detection and capitalization
        sentences = re.split(r'(\.|\?|\!)\s+', text)
        result = []
        
        for i in range(0, len(sentences), 2):
            if i < len(sentences):
                # Get the sentence and capitalize first letter
                sentence = sentences[i]
                if sentence and len(sentence) > 0:
                    sentence = sentence[0].upper() + sentence[1:]
                    
                result.append(sentence)
                
                # Add punctuation and space if available
                if i + 1 < len(sentences):
                    result.append(sentences[i+1] + ' ')
                    
        return ''.join(result)
        
    def _detect_urls(self, text: str) -> str:
        """
        Detect and format URLs in text
        
        Args:
            text: Input text
            
        Returns:
            Text with formatted URLs
        """
        # Simple URL detection - in a real plugin this would be more sophisticated
        url_pattern = r'(https?://[^\s]+)'
        return re.sub(url_pattern, r'<\1>', text)
        
    def on_shutdown(self) -> None:
        """Clean up when plugin is shut down"""
        logger.info("Text Formatter plugin shutting down")
