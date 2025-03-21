# ai-test-automation/aiqatester/analyzer/element_finder.py
"""
Element Finder module for AIQATester.

This module finds and classifies UI elements on web pages.
"""

from typing import Dict, List, Optional, Any

from loguru import logger

from aiqatester.browser.controller import BrowserController

class ElementFinder:
    """Finds and classifies UI elements on web pages."""
    
    def __init__(self, browser_controller: BrowserController):
        """
        Initialize the element finder.
        
        Args:
            browser_controller: Browser controller instance
        """
        self.browser = browser_controller
        logger.info("ElementFinder initialized")
        
    async def find_interactive_elements(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Find all interactive elements on the current page.
        
        Returns:
            Dictionary of interactive elements grouped by type
        """
        return await self.browser.extract_interactive_elements()
    
    async def find_elements_by_type(self, element_type: str) -> List[Dict[str, Any]]:
        """
        Find elements of a specific type.
        
        Args:
            element_type: Type of elements to find
            
        Returns:
            List of elements of the specified type
        """
        elements = await self.find_interactive_elements()
        return elements.get(element_type, [])
    
    async def find_element_by_text(self, text: str, element_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find an element by its text content.
        
        Args:
            text: Text to search for
            element_type: Optional type of element to search within
            
        Returns:
            Element if found, None otherwise
        """
        elements = await self.find_interactive_elements()
        
        # If element_type is specified, only search within that type
        if element_type:
            element_list = elements.get(element_type, [])
            for element in element_list:
                if 'text' in element and element['text'] and text in element['text']:
                    return element
            return None
        
        # Otherwise, search in all element types
        for element_type, element_list in elements.items():
            for element in element_list:
                if 'text' in element and element['text'] and text in element['text']:
                    return element
        
        return None
    
    async def find_input_by_label(self, label_text: str) -> Optional[Dict[str, Any]]:
        """
        Find an input field by its associated label text.
        
        Args:
            label_text: Text of the label to search for
            
        Returns:
            Input element if found, None otherwise
        """
        # First try to find the label element
        label_selectors = [
            f"label:text-is('{label_text}')",
            f"label:text-contains('{label_text}')"
        ]
        
        for selector in label_selectors:
            try:
                label_element = await self.browser.page.query_selector(selector)
                if label_element:
                    # Get the 'for' attribute
                    for_attr = await label_element.get_attribute('for')
                    if for_attr:
                        # Find the input with this ID
                        input_element = await self.browser.page.query_selector(f"#{for_attr}")
                        if input_element:
                            # Get input details
                            input_id = for_attr
                            input_name = await input_element.get_attribute('name')
                            input_type = await input_element.get_attribute('type') or 'text'
                            
                            return {
                                'id': input_id,
                                'name': input_name,
                                'type': input_type
                            }
            except Exception as e:
                logger.debug(f"Error finding input by label '{label_text}': {e}")
        
        return None
    
    async def find_form_elements(self) -> Dict[str, Any]:
        """
        Find and analyze form elements on the page.
        
        Returns:
            Dictionary containing form elements and their attributes
        """
        forms = {}
        
        # Find all forms
        form_elements = await self.browser.page.query_selector_all('form')
        
        for i, form in enumerate(form_elements):
            form_id = await form.get_attribute('id') or f"form_{i}"
            form_action = await form.get_attribute('action') or ""
            form_method = await form.get_attribute('method') or "get"
            
            # Find inputs, selects, textareas within the form
            form_inputs = []
            
            # Inputs
            input_elements = await form.query_selector_all('input')
            for input_elem in input_elements:
                input_type = await input_elem.get_attribute('type') or 'text'
                input_name = await input_elem.get_attribute('name')
                input_id = await input_elem.get_attribute('id')
                input_required = await input_elem.get_attribute('required') is not None
                
                form_inputs.append({
                    'type': input_type,
                    'name': input_name,
                    'id': input_id,
                    'required': input_required
                })
            
            # Selects
            select_elements = await form.query_selector_all('select')
            for select_elem in select_elements:
                select_name = await select_elem.get_attribute('name')
                select_id = await select_elem.get_attribute('id')
                select_required = await select_elem.get_attribute('required') is not None
                
                # Get options
                options = []
                option_elements = await select_elem.query_selector_all('option')
                for option in option_elements:
                    option_value = await option.get_attribute('value')
                    option_text = await option.text_content()
                    options.append({
                        'value': option_value,
                        'text': option_text
                    })
                
                form_inputs.append({
                    'type': 'select',
                    'name': select_name,
                    'id': select_id,
                    'required': select_required,
                    'options': options
                })
            
            # Textareas
            textarea_elements = await form.query_selector_all('textarea')
            for textarea in textarea_elements:
                textarea_name = await textarea.get_attribute('name')
                textarea_id = await textarea.get_attribute('id')
                textarea_required = await textarea.get_attribute('required') is not None
                
                form_inputs.append({
                    'type': 'textarea',
                    'name': textarea_name,
                    'id': textarea_id,
                    'required': textarea_required
                })
            
            # Add to forms dictionary
            forms[form_id] = {
                'id': form_id,
                'action': form_action,
                'method': form_method,
                'inputs': form_inputs
            }
        
        return forms