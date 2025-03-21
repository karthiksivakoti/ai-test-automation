# ai-test-automation/aiqatester/browser/actions.py
"""
Browser Actions module for AIQATester.

This module defines common browser actions for test execution.
"""

from typing import Dict, List, Optional, Any, Union

from loguru import logger

from aiqatester.browser.controller import BrowserController

class BrowserActions:
    """Common browser actions for test execution."""
    
    def __init__(self, browser_controller: BrowserController):
        """
        Initialize the browser actions.
        
        Args:
            browser_controller: Browser controller instance
        """
        self.browser = browser_controller
        logger.info("BrowserActions initialized")
        
    async def navigate_to(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            await self.browser.navigate(url)
            return True
        except Exception as e:
            logger.error(f"Navigation failed to {url}: {e}")
            return False
        
    async def click_element(self, selector: str) -> bool:
        """
        Click on an element.
        
        Args:
            selector: Element selector
            
        Returns:
            True if click was successful, False otherwise
        """
        return await self.browser.click(selector)
        
    async def fill_input(self, selector: str, value: str) -> bool:
        """
        Fill an input field.
        
        Args:
            selector: Input field selector
            value: Value to fill
            
        Returns:
            True if fill was successful, False otherwise
        """
        return await self.browser.type_text(selector, value)
        
    async def select_option(self, selector: str, value: Optional[str] = None, label: Optional[str] = None) -> bool:
        """
        Select an option from a dropdown.
        
        Args:
            selector: Dropdown selector
            value: Option value to select
            label: Option label to select
            
        Returns:
            True if selection was successful, False otherwise
        """
        return await self.browser.select_option(selector, value=value, label=label)
        
    async def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for an element to be visible.
        
        Args:
            selector: Element selector
            timeout: Wait timeout in milliseconds
            
        Returns:
            True if element became visible, False otherwise
        """
        return await self.browser.wait_for_selector(selector, timeout=timeout)
        
    async def get_element_text(self, selector: str) -> Optional[str]:
        """
        Get text from an element.
        
        Args:
            selector: Element selector
            
        Returns:
            Element text if found, None otherwise
        """
        return await self.browser.get_element_text(selector)
        
    async def check_element_exists(self, selector: str) -> bool:
        """
        Check if an element exists on the page.
        
        Args:
            selector: Element selector
            
        Returns:
            True if element exists, False otherwise
        """
        element = await self.browser.get_element_by_selector(selector)
        return element is not None
        
    async def execute_action_sequence(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a sequence of browser actions.
        
        Args:
            actions: List of action dictionaries, each containing:
                - action_type: Type of action (navigate, click, fill, etc.)
                - selector: Element selector (optional)
                - value: Value to use (optional)
                - etc.
                
        Returns:
            Dictionary containing results of each action
        """
        results = {}
        
        for i, action in enumerate(actions):
            action_type = action.get("action_type")
            selector = action.get("selector")
            value = action.get("value")
            
            result = False
            
            if action_type == "navigate":
                result = await self.navigate_to(value)
            elif action_type == "click":
                result = await self.click_element(selector)
            elif action_type == "fill":
                result = await self.fill_input(selector, value)
            elif action_type == "select":
                result = await self.select_option(selector, value=value)
            elif action_type == "wait":
                result = await self.wait_for_element(selector)
            else:
                logger.warning(f"Unknown action type: {action_type}")
                
            results[f"action_{i}"] = {
                "action_type": action_type,
                "success": result
            }
            
            # If action failed, log and stop sequence
            if not result:
                logger.error(f"Action sequence failed at step {i}: {action_type}")
                break
                
        return results