# ai-test-automation/aiqatester/executor/screenshot.py
"""
Screenshot Manager module for AIQATester.

This module captures and manages screenshots during test execution.
"""

from typing import Dict, List, Optional, Any
import os
import datetime

from loguru import logger

from aiqatester.browser.controller import BrowserController

class ScreenshotManager:
    """Captures and manages screenshots during test execution."""
    
    def __init__(self, browser_controller: BrowserController, screenshot_dir: str = "screenshots"):
        """
        Initialize the screenshot manager.
        
        Args:
            browser_controller: Browser controller instance
            screenshot_dir: Directory to save screenshots
        """
        self.browser = browser_controller
        self.screenshot_dir = screenshot_dir
        
        # Create screenshot directory if it doesn't exist
        os.makedirs(screenshot_dir, exist_ok=True)
        
        logger.info("ScreenshotManager initialized")
        
    async def capture_screenshot(self, name: Optional[str] = None, full_page: bool = True) -> str:
        """
        Capture a screenshot.
        
        Args:
            name: Optional name for the screenshot
            full_page: Whether to capture the full page
            
        Returns:
            Path to the saved screenshot
        """
        if name is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"screenshot_{timestamp}"
            
        return await self.browser.take_screenshot(name, full_page)
    
    async def capture_element_screenshot(self, selector: str, name: Optional[str] = None) -> Optional[str]:
        """
        Capture a screenshot of a specific element.
        
        Args:
            selector: CSS selector for the element
            name: Optional name for the screenshot
            
        Returns:
            Path to the saved screenshot, or None if element not found
        """
        try:
            element = await self.browser.get_element_by_selector(selector)
            if not element:
                logger.warning(f"Element not found for screenshot: {selector}")
                return None
            
            if name is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                name = f"element_{timestamp}"
            
            file_path = os.path.join(self.screenshot_dir, f"{name}.png")
            
            await element.screenshot(path=file_path)
            logger.info(f"Element screenshot saved to {file_path}")
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error capturing element screenshot: {e}")
            return None
    
    def get_screenshots(self, test_name: str) -> List[str]:
        """
        Get all screenshots for a specific test.
        
        Args:
            test_name: Name of the test
            
        Returns:
            List of screenshot paths
        """
        screenshots = []
        
        # Replace spaces with underscores in test name
        test_name_normalized = test_name.replace(" ", "_")
        
        # Find all screenshots matching the test name
        for filename in os.listdir(self.screenshot_dir):
            if filename.startswith(f"test_{test_name_normalized}_") and filename.endswith(".png"):
                screenshots.append(os.path.join(self.screenshot_dir, filename))
        
        return screenshots
    
    def clean_screenshots(self, older_than_days: int = 7) -> int:
        """
        Clean up old screenshots.
        
        Args:
            older_than_days: Delete screenshots older than this many days
            
        Returns:
            Number of deleted screenshots
        """
        import time
        
        # Calculate cutoff time
        cutoff_time = time.time() - (older_than_days * 24 * 60 * 60)
        deleted_count = 0
        
        # Delete old screenshots
        for filename in os.listdir(self.screenshot_dir):
            if filename.endswith(".png"):
                file_path = os.path.join(self.screenshot_dir, filename)
                file_mtime = os.path.getmtime(file_path)
                
                if file_mtime < cutoff_time:
                    os.remove(file_path)
                    deleted_count += 1
        
        logger.info(f"Deleted {deleted_count} old screenshots")
        return deleted_count