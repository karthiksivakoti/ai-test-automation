# ai-test-automation/aiqatester/utils/html_utils.py
"""
HTML Utilities module for AIQATester.

This module provides utilities for working with HTML content.
"""

from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import html2text
from bs4.element import Comment

def clean_html(html: str) -> str:
    """
    Clean and normalize HTML content.
    
    Args:
        html: HTML content to clean
        
    Returns:
        Cleaned HTML
    """
    soup = BeautifulSoup(html, "lxml")
    
    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # Remove script and style tags
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    # Return pretty-printed HTML
    return soup.prettify()

def html_to_text(html: str) -> str:
    """
    Convert HTML to plain text.
    
    Args:
        html: HTML content to convert
        
    Returns:
        Plain text
    """
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_tables = False
    h.unicode_snob = True
    return h.handle(html)

def extract_form_elements(html: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract form elements from HTML.
    
    Args:
        html: HTML content
        
    Returns:
        Dictionary of form elements grouped by form
    """
    soup = BeautifulSoup(html, "lxml")
    forms = {}
    
    for i, form in enumerate(soup.find_all("form")):
        form_id = form.get("id", f"form_{i}")
        forms[form_id] = {
            "id": form_id,
            "action": form.get("action", ""),
            "method": form.get("method", "get"),
            "inputs": []
        }
        
        for input_tag in form.find_all(["input", "textarea", "select"]):
            input_info = {
                "name": input_tag.get("name", ""),
                "id": input_tag.get("id", ""),
                "type": input_tag.get("type", "") if input_tag.name == "input" else input_tag.name,
                "required": input_tag.has_attr("required")
            }
            
            forms[form_id]["inputs"].append(input_info)
    
    return forms

def extract_elements_by_type(html: str, element_type: str) -> List[Dict[str, Any]]:
    """
    Extract elements of a specific type from HTML.
    
    Args:
        html: HTML content
        element_type: Type of element to extract (e.g., 'a', 'button', 'input')
        
    Returns:
        List of extracted elements
    """
    soup = BeautifulSoup(html, "lxml")
    elements = []
    
    for element in soup.find_all(element_type):
        element_info = {attr: element.get(attr) for attr in element.attrs}
        
        # Add text content if available
        if element.string:
            element_info["text"] = element.string.strip()
        
        elements.append(element_info)
    
    return elements

def find_element_by_text(html: str, text: str, element_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Find an element by its text content.
    
    Args:
        html: HTML content
        text: Text to search for
        element_type: Optional type of element to search (e.g., 'a', 'button')
        
    Returns:
        Element if found, None otherwise
    """
    soup = BeautifulSoup(html, "lxml")
    
    # Find elements containing the text
    if element_type:
        elements = soup.find_all(element_type, string=lambda s: text in s if s else False)
    else:
        elements = soup.find_all(string=lambda s: text in s if s else False)
        elements = [element.parent for element in elements]
    
    if not elements:
        return None
    
    # Get the first matching element
    element = elements[0]
    
    # Extract element info
    element_info = {attr: element.get(attr) for attr in element.attrs}
    
    # Add tag name and text content
    element_info["tag"] = element.name
    element_info["text"] = element.text.strip()
    
    return element_info

def get_element_xpath(html: str, element_id: str = None, element_class: str = None, element_text: str = None) -> Optional[str]:
    """
    Generate an XPath for an element based on its attributes.
    
    Args:
        html: HTML content
        element_id: Element ID
        element_class: Element class
        element_text: Element text content
        
    Returns:
        XPath expression, or None if element not found
    """
    soup = BeautifulSoup(html, "lxml")
    element = None
    
    # Find element by ID
    if element_id:
        element = soup.find(id=element_id)
    
    # Find element by class
    elif element_class:
        element = soup.find(class_=element_class)
    
    # Find element by text content
    elif element_text:
        element = soup.find(string=lambda s: element_text in s if s else False)
        if element:
            element = element.parent
    
    if not element:
        return None
    
    # Generate XPath
    components = []
    child = element
    
    while child:
        siblings = child.parent.find_all(child.name, recursive=False) if child.parent else []
        if len(siblings) > 1:
            index = siblings.index(child) + 1
            components.append(f"{child.name}[{index}]")
        else:
            components.append(child.name)
        
        child = child.parent
        if child is None or child.name == "html":
            break
    
    # Reverse the order to get the correct path
    xpath = "//" + "/".join(reversed(components))
    
    return xpath