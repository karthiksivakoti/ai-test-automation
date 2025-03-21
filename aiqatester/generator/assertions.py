# ai-test-automation/aiqatester/generator/assertions.py
"""
Assertion Builder module for AIQATester.

This module builds test assertions for verifying test results.
"""

from typing import Dict, List, Any

from loguru import logger

class AssertionBuilder:
    """Builds test assertions for verifying test results."""
    
    def __init__(self):
        """Initialize the assertion builder."""
        logger.info("AssertionBuilder initialized")
        
    def build_assertions(self, test_case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build assertions for a test case.
        
        Args:
            test_case: The test case to build assertions for
            
        Returns:
            List of assertions
        """
        assertions = []
        
        # Extract expected results from test case
        expected_results = test_case.get("expected_results", [])
        if not expected_results:
            logger.warning(f"No expected results found for test case: {test_case.get('name', 'Unknown')}")
            return self._build_default_assertions(test_case)
        
        # Convert expected results to assertions
        for i, result in enumerate(expected_results):
            # Skip empty results
            if not result:
                continue
                
            # Create assertion based on result text
            assertion = self._create_assertion_from_result(result, i, test_case)
            assertions.append(assertion)
        
        # If no assertions were created, build default assertions
        if not assertions:
            assertions = self._build_default_assertions(test_case)
        
        logger.info(f"Built {len(assertions)} assertions for test case: {test_case.get('name', 'Unknown')}")
        return assertions
    
    def _create_assertion_from_result(self, result: str, index: int, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an assertion from an expected result.
        
        Args:
            result: Expected result text
            index: Result index
            test_case: Test case information
            
        Returns:
            Assertion object
        """
        result_lower = result.lower()
        steps = test_case.get("steps", [])
        
        # Try to determine assertion type and element
        assertion_type = "element_exists"
        element = None
        expected = True
        
        # Determine assertion based on result text
        if "page" in result_lower and "navigated" in result_lower:
            assertion_type = "page_url"
            # Try to find the URL in the result
            import re
            url_match = re.search(r'to\s+([^\s]+)', result)
            expected = url_match.group(1) if url_match else None
        
        elif "displayed" in result_lower or "visible" in result_lower or "shown" in result_lower:
            assertion_type = "element_visible"
            
            # Try to find what element should be visible
            # Check if any common elements are mentioned
            elements = ["button", "link", "input", "form", "message", "error", "success"]
            for elem in elements:
                if elem in result_lower:
                    # Try to find the element in the steps
                    for step in steps:
                        step_text = step.get("action", "") if isinstance(step, dict) else str(step)
                        if elem in step_text.lower():
                            # Use this step's selector
                            element = step.get("selector") or step.get("element")
                            break
                    break
        
        elif "not" in result_lower and ("displayed" in result_lower or "visible" in result_lower):
            assertion_type = "element_not_visible"
            expected = False
            
            # Same logic as above
            elements = ["button", "link", "input", "form", "message", "error", "success"]
            for elem in elements:
                if elem in result_lower:
                    for step in steps:
                        step_text = step.get("action", "") if isinstance(step, dict) else str(step)
                        if elem in step_text.lower():
                            element = step.get("selector") or step.get("element")
                            break
                    break
        
        elif "contains" in result_lower or "text" in result_lower:
            assertion_type = "element_text"
            
            # Try to find the text to check for
            import re
            text_match = re.search(r'text[:\s]+"([^"]+)"', result_lower)
            if text_match:
                expected = text_match.group(1)
                
                # Try to find the element
                for step in steps:
                    step_text = step.get("action", "") if isinstance(step, dict) else str(step)
                    if expected.lower() in step_text.lower():
                        element = step.get("selector") or step.get("element")
                        break
            else:
                # Try another pattern
                text_match = re.search(r'contains[:\s]+["\'](.*?)["\']', result_lower)
                if text_match:
                    expected = text_match.group(1)
        
        # Create the assertion
        assertion = {
            "id": f"assertion_{index + 1}",
            "type": assertion_type,
            "element": element,
            "expected": expected,
            "description": result
        }
        
        return assertion
    
    def _build_default_assertions(self, test_case: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build default assertions for a test case.
        
        Args:
            test_case: Test case information
            
        Returns:
            List of default assertions
        """
        assertions = []
        steps = test_case.get("steps", [])
        
        # Add default assertions based on steps
        for i, step in enumerate(steps):
            # Skip if not a dict
            if not isinstance(step, dict):
                continue
                
            # Get action and selector
            action = step.get("action", "").lower()
            selector = step.get("selector") or step.get("element")
            
            # Skip if no selector
            if not selector:
                continue
                
            # Determine assertion type based on action
            if "click" in action:
                # After clicking, the element should still exist
                assertions.append({
                    "id": f"assertion_click_{i + 1}",
                    "type": "element_exists",
                    "element": selector,
                    "expected": True,
                    "description": f"Verify element exists after clicking it in step {i + 1}"
                })
            
            elif "type" in action or "fill" in action or "input" in action:
                # After typing, the element should have the value
                value = step.get("value", "")
                assertions.append({
                    "id": f"assertion_input_{i + 1}",
                    "type": "element_value",
                    "element": selector,
                    "expected": value,
                    "description": f"Verify input value after step {i + 1}"
                })
            
            elif "select" in action:
                # After selecting, the option should be selected
                value = step.get("value", "")
                assertions.append({
                    "id": f"assertion_select_{i + 1}",
                    "type": "element_selected",
                    "element": selector,
                    "expected": value,
                    "description": f"Verify selected option after step {i + 1}"
                })
            
            elif "navigate" in action or "go to" in action:
                # After navigating, the URL should be correct
                url = step.get("value", "")
                if url:
                    assertions.append({
                        "id": f"assertion_url_{i + 1}",
                        "type": "page_url",
                        "element": None,
                        "expected": url,
                        "description": f"Verify URL after navigation in step {i + 1}"
                    })
        
        return assertions