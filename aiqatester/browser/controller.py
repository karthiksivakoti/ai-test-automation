# ai-test-automation/aiqatester/browser/controller.py
"""
Browser Controller module for AIQATester.

This module provides browser automation capabilities using Playwright.
It handles browser initialization, navigation, and various interactions
with web elements.
"""

import asyncio
import os
import time
import re
from typing import Dict, List, Optional, Tuple, Union, Any

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, ElementHandle
from loguru import logger
from bs4 import BeautifulSoup
import html2text

class BrowserController:
    """Controls browser interactions for website testing."""
    
    def __init__(
        self, 
        headless: bool = True,
        browser_type: str = "chromium",
        slow_mo: int = 50,
        viewport_size: Dict[str, int] = {"width": 1280, "height": 720},
        timeout: int = 30000,
        screenshot_dir: str = "screenshots"
    ):
        """
        Initialize the browser controller.
        
        Args:
            headless: Whether to run the browser in headless mode
            browser_type: Type of browser to use ('chromium', 'firefox', 'webkit')
            slow_mo: Slow down operations by specified milliseconds (helps with stability)
            viewport_size: Browser viewport dimensions
            timeout: Default timeout for operations in milliseconds
            screenshot_dir: Directory to save screenshots
        """
        self.headless = headless
        self.browser_type = browser_type
        self.slow_mo = slow_mo
        self.viewport_size = viewport_size
        self.timeout = timeout
        self.screenshot_dir = screenshot_dir
        
        # Will be initialized in start() method
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.pages = []
        
        # Create screenshot directory if it doesn't exist
        os.makedirs(screenshot_dir, exist_ok=True)
        
        logger.info(f"Initialized BrowserController with {browser_type} browser")

    async def start(self) -> None:
        """Start the browser and create a new context and page."""
        self.playwright = await async_playwright().start()
        
        # Select browser based on browser_type
        if self.browser_type == "chromium":
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )
        elif self.browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )
        elif self.browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )
        else:
            raise ValueError(f"Unsupported browser type: {self.browser_type}")
        
        # Create a persistent context for better cookie/session management
        self.context = await self.browser.new_context(
            viewport=self.viewport_size,
            accept_downloads=True
        )
        
        # Set default timeout
        self.context.set_default_timeout(self.timeout)
        
        # Create a new page
        self.page = await self.context.new_page()
        self.pages = [self.page]
        
        # Setup event listeners
        await self._setup_listeners()
        
        logger.info(f"Started {self.browser_type} browser")

    async def _setup_listeners(self) -> None:
        """Set up event listeners for the page."""
        # Log console messages
        self.page.on("console", lambda msg: logger.debug(f"Console {msg.type}: {msg.text}"))
        
        # Log errors
        self.page.on("pageerror", lambda err: logger.error(f"Page error: {err}"))
        
        # Log requests (debug level)
        self.page.on("request", lambda request: logger.debug(f"Request: {request.method} {request.url}"))
        
        # Log response errors (warning level or above)
        async def handle_response(response):
            if response.status >= 400:
                logger.warning(f"Response error: {response.status} {response.url}")
        
        self.page.on("response", handle_response)

    async def stop(self) -> None:
        """Close the browser and all resources."""
        if self.page:
            await self.page.close()
            self.page = None
        
        if self.context:
            await self.context.close()
            self.context = None
        
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        
        logger.info("Browser stopped and resources released")

    async def navigate(self, url: str, wait_until: str = "networkidle") -> None:
        """
        Navigate to a URL and wait for the page to load.
        
        Args:
            url: The URL to navigate to
            wait_until: Navigation wait condition ('domcontentloaded', 'load', 'networkidle')
        """
        try:
            response = await self.page.goto(url, wait_until=wait_until, timeout=self.timeout)
            if response:
                logger.info(f"Navigated to {url} (Status: {response.status})")
            else:
                logger.warning(f"Navigation to {url} did not return a response")
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            await self.take_screenshot(f"navigation_error_{int(time.time())}")
            raise

    async def take_screenshot(self, name: str = None, full_page: bool = True) -> str:
        """
        Take a screenshot of the current page.
        
        Args:
            name: Name for the screenshot file (without extension)
            full_page: Whether to capture the full scrollable page
            
        Returns:
            Path to the saved screenshot
        """
        if name is None:
            name = f"screenshot_{int(time.time())}"
        
        file_path = os.path.join(self.screenshot_dir, f"{name}.png")
        
        await self.page.screenshot(path=file_path, full_page=full_page)
        logger.info(f"Screenshot saved to {file_path}")
        
        return file_path

    async def get_html(self) -> str:
        """Get the HTML content of the current page."""
        return await self.page.content()

    async def get_page_text(self) -> str:
        """
        Get the text content of the current page.
        Returns the text in a human-readable format.
        """
        html_content = await self.get_html()
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        return h.handle(html_content)

    async def get_element_by_selector(self, selector: str) -> Optional[ElementHandle]:
        """
        Get an element by CSS selector.
        
        Args:
            selector: CSS selector to find the element
            
        Returns:
            ElementHandle if found, None otherwise
        """
        try:
            element = await self.page.wait_for_selector(selector, state="attached", timeout=self.timeout)
            return element
        except Exception as e:
            logger.debug(f"Element not found with selector '{selector}': {e}")
            return None

    async def click(self, selector: str, timeout: int = None) -> bool:
        """
        Click on an element identified by the selector.
        
        Args:
            selector: CSS selector to find the element
            timeout: Custom timeout in milliseconds
            
        Returns:
            True if click was successful, False otherwise
        """
        try:
            timeout = timeout or self.timeout
            await self.page.click(selector, timeout=timeout)
            logger.info(f"Clicked on element: {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to click on {selector}: {e}")
            await self.take_screenshot(f"click_error_{int(time.time())}")
            return False

    async def type_text(self, selector: str, text: str, delay: int = 20) -> bool:
        """
        Type text into an input element.
        
        Args:
            selector: CSS selector to find the element
            text: Text to type
            delay: Delay between keystrokes in milliseconds
            
        Returns:
            True if typing was successful, False otherwise
        """
        try:
            await self.page.fill(selector, "")  # Clear existing text
            await self.page.type(selector, text, delay=delay)
            logger.info(f"Typed text into {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to type text into {selector}: {e}")
            await self.take_screenshot(f"type_error_{int(time.time())}")
            return False

    async def select_option(self, selector: str, value: str = None, label: str = None, index: int = None) -> bool:
        """
        Select an option from a select element.
        
        Args:
            selector: CSS selector for the select element
            value: Value of the option to select
            label: Label of the option to select
            index: Index of the option to select
            
        Returns:
            True if selection was successful, False otherwise
        """
        try:
            if value:
                await self.page.select_option(selector, value=value)
            elif label:
                await self.page.select_option(selector, label=label)
            elif index is not None:
                await self.page.select_option(selector, index=index)
            else:
                raise ValueError("Must provide one of: value, label, or index")
            
            logger.info(f"Selected option in {selector}")
            return True
        except Exception as e:
            logger.error(f"Failed to select option in {selector}: {e}")
            await self.take_screenshot(f"select_error_{int(time.time())}")
            return False

    async def get_element_text(self, selector: str) -> Optional[str]:
        """
        Get the text content of an element.
        
        Args:
            selector: CSS selector to find the element
            
        Returns:
            Text content of the element if found, None otherwise
        """
        try:
            element = await self.get_element_by_selector(selector)
            if element:
                return await element.text_content()
            return None
        except Exception as e:
            logger.error(f"Failed to get text from {selector}: {e}")
            return None

    async def wait_for_navigation(self, timeout: int = None, wait_until: str = "networkidle") -> bool:
        """
        Wait for navigation to complete.
        
        Args:
            timeout: Custom timeout in milliseconds
            wait_until: Navigation wait condition
            
        Returns:
            True if navigation completed successfully, False otherwise
        """
        try:
            timeout = timeout or self.timeout
            await self.page.wait_for_load_state(wait_until, timeout=timeout)
            logger.info(f"Navigation completed (wait_until: {wait_until})")
            return True
        except Exception as e:
            logger.error(f"Navigation timeout: {e}")
            await self.take_screenshot(f"navigation_timeout_{int(time.time())}")
            return False

    async def wait_for_selector(self, selector: str, timeout: int = None, state: str = "visible") -> bool:
        """
        Wait for an element to be visible.
        
        Args:
            selector: CSS selector to find the element
            timeout: Custom timeout in milliseconds
            state: State to wait for ('attached', 'detached', 'visible', 'hidden')
            
        Returns:
            True if element was found, False otherwise
        """
        try:
            timeout = timeout or self.timeout
            await self.page.wait_for_selector(selector, timeout=timeout, state=state)
            logger.info(f"Element found: {selector} (state: {state})")
            return True
        except Exception as e:
            logger.error(f"Timeout waiting for {selector} (state: {state}): {e}")
            await self.take_screenshot(f"wait_selector_error_{int(time.time())}")
            return False

    async def get_all_text_elements(self) -> Dict[str, str]:
        """
        Get all text elements on the page with their selectors.
        Useful for LLMs to understand page content and structure.
        
        Returns:
            Dictionary mapping selectors to their text content
        """
        selectors = {
            "headings": "h1, h2, h3, h4, h5, h6",
            "links": "a",
            "buttons": "button, input[type='button'], input[type='submit']",
            "inputs": "input[type='text'], input[type='email'], input[type='password'], textarea",
            "paragraphs": "p",
            "list_items": "li"
        }
        
        result = {}
        
        for element_type, selector in selectors.items():
            elements = await self.page.query_selector_all(selector)
            
            for i, element in enumerate(elements):
                try:
                    text = await element.text_content()
                    text = text.strip()
                    if text:
                        # Create a unique key for this element
                        key = f"{element_type}_{i}"
                        result[key] = text
                except Exception as e:
                    logger.debug(f"Failed to get text from {element_type} #{i}: {e}")
        
        return result
    
    async def extract_interactive_elements(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Extract all interactive elements on the page.
        Useful for automated test generation.
        
        Returns:
            Dictionary with lists of interactive elements grouped by type
        """
        interactive_elements = {
            "links": [],
            "buttons": [],
            "inputs": [],
            "selects": [],
            "checkboxes": [],
            "radios": []
        }
        
        # Extract links
        links = await self.page.query_selector_all("a[href]")
        for link in links:
            try:
                href = await link.get_attribute("href")
                text = await link.text_content()
                id_attr = await link.get_attribute("id")
                class_attr = await link.get_attribute("class")
                
                interactive_elements["links"].append({
                    "text": text.strip(),
                    "href": href,
                    "id": id_attr,
                    "class": class_attr,
                })
            except Exception as e:
                logger.debug(f"Failed to extract link: {e}")
        
        # Extract buttons
        buttons = await self.page.query_selector_all("button, input[type='button'], input[type='submit']")
        for button in buttons:
            try:
                text = await button.text_content()
                if not text:
                    text = await button.get_attribute("value")
                id_attr = await button.get_attribute("id")
                class_attr = await button.get_attribute("class")
                
                interactive_elements["buttons"].append({
                    "text": text.strip() if text else "",
                    "id": id_attr,
                    "class": class_attr,
                })
            except Exception as e:
                logger.debug(f"Failed to extract button: {e}")
        
        # Extract inputs
        inputs = await self.page.query_selector_all("input[type='text'], input[type='email'], input[type='password'], textarea")
        for input_elem in inputs:
            try:
                name = await input_elem.get_attribute("name")
                id_attr = await input_elem.get_attribute("id")
                placeholder = await input_elem.get_attribute("placeholder")
                input_type = await input_elem.get_attribute("type") or "text"
                
                interactive_elements["inputs"].append({
                    "name": name,
                    "id": id_attr,
                    "placeholder": placeholder,
                    "type": input_type
                })
            except Exception as e:
                logger.debug(f"Failed to extract input: {e}")
        
        # Extract select elements
        selects = await self.page.query_selector_all("select")
        for select in selects:
            try:
                name = await select.get_attribute("name")
                id_attr = await select.get_attribute("id")
                
                interactive_elements["selects"].append({
                    "name": name,
                    "id": id_attr
                })
            except Exception as e:
                logger.debug(f"Failed to extract select: {e}")
        
        # Extract checkboxes
        checkboxes = await self.page.query_selector_all("input[type='checkbox']")
        for checkbox in checkboxes:
            try:
                name = await checkbox.get_attribute("name")
                id_attr = await checkbox.get_attribute("id")
                
                interactive_elements["checkboxes"].append({
                    "name": name,
                    "id": id_attr
                })
            except Exception as e:
                logger.debug(f"Failed to extract checkbox: {e}")
        
        # Extract radio buttons
        radios = await self.page.query_selector_all("input[type='radio']")
        for radio in radios:
            try:
                name = await radio.get_attribute("name")
                id_attr = await radio.get_attribute("id")
                value = await radio.get_attribute("value")
                
                interactive_elements["radios"].append({
                    "name": name,
                    "id": id_attr,
                    "value": value
                })
            except Exception as e:
                logger.debug(f"Failed to extract radio: {e}")
        
        return interactive_elements