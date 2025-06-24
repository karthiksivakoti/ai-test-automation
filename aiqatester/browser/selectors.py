# aiqatester/browser/selectors.py
"""
Selector Utilities module for AIQATester.

This module provides utilities for working with selectors.
"""

from typing import Dict, List, Optional, Any
import re

class SelectorUtils:
    """Utilities for working with selectors."""
    
    @staticmethod
    def create_selector(element_data: Dict[str, Any]) -> str:
        """
        Create a selector for an element based on its data.
        
        Args:
            element_data: Element data
            
        Returns:
            CSS selector
        """
        selectors = []
        
        # Try to create selectors based on available attributes
        if element_data.get("id"):
            selectors.append(f"#{element_data['id']}")
        
        if element_data.get("class"):
            class_selector = "." + ".".join(element_data["class"].split())
            selectors.append(class_selector)
        
        if element_data.get("name"):
            selectors.append(f"[name='{element_data['name']}']")
        
        if element_data.get("type"):
            selectors.append(f"[type='{element_data['type']}']")
        
        if element_data.get("text"):
            # This is a simplification - text selection is complex
            text = element_data["text"].strip()
            if text:
                # For links and buttons, use text content
                selectors.append(f"a:text('{text}')")
                selectors.append(f"button:text('{text}')")
        
        # Return the most specific selector (usually the first one)
        return selectors[0] if selectors else ""
    
    @staticmethod
    def sanitize_selector(selector: str) -> str:
        """
        Sanitize a selector to make it more robust.
        
        Args:
            selector: CSS selector to sanitize
            
        Returns:
            Sanitized selector
        """
        # Remove unnecessary whitespace
        selector = re.sub(r'\s+', ' ', selector).strip()
        
        # Escape single quotes in attribute selectors
        selector = re.sub(
            r"\[([^\]=]+)='([^']*)'\]",
            lambda m: "[" + m.group(1) + "='" + m.group(2).replace("'", r"\\'") + "']",
            selector
        )
        
        return selector
    
    @staticmethod
    def combine_selectors(selectors: List[str]) -> str:
        """
        Combine multiple selectors into a single selector.
        
        Args:
            selectors: List of selectors to combine
            
        Returns:
            Combined selector
        """
        if not selectors:
            return ""
            
        # Remove any empty selectors
        valid_selectors = [s for s in selectors if s]
        
        if not valid_selectors:
            return ""
            
        # Join selectors with comma for OR relationship
        return ", ".join(valid_selectors)
    
    @staticmethod
    def create_xpath(element_data: Dict[str, Any]) -> str:
        """
        Create an XPath expression for an element based on its data.
        
        Args:
            element_data: Element data
            
        Returns:
            XPath expression
        """
        xpath_parts = []
        
        # Start with a generic element selector
        element_type = element_data.get("type", "")
        
        if element_type == "button" or element_type == "submit":
            base = "//button"
        elif element_type == "text" or element_type == "email" or element_type == "password":
            base = "//input"
        elif element_type == "select":
            base = "//select"
        elif element_type.startswith("h") and len(element_type) == 2 and element_type[1].isdigit():
            # heading h1-h6
            base = f"//{element_type}"
        else:
            base = "//*"
            
        # Add attribute conditions
        conditions = []
        
        if element_data.get("id"):
            conditions.append(f"@id='{element_data['id']}'")
            
        if element_data.get("name"):
            conditions.append(f"@name='{element_data['name']}'")
            
        if element_data.get("class"):
            conditions.append(f"contains(@class, '{element_data['class']}')")
            
        if element_data.get("type"):
            conditions.append(f"@type='{element_data['type']}'")
            
        if element_data.get("text"):
            text = element_data["text"].strip()
            if text:
                conditions.append(f"text()='{text}' or contains(text(), '{text}')")
                
        # Combine base and conditions
        if conditions:
            xpath = f"{base}[{' and '.join(conditions)}]"
        else:
            xpath = base
            
        return xpath