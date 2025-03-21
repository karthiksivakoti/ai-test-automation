# ai-test-automation/aiqatester/generator/script_generator.py
"""
Script Generator module for AIQATester.

This module generates executable test scripts based on testing strategies.
"""

from typing import Dict, List, Optional, Any

from loguru import logger

from aiqatester.llm.openai_client import OpenAIClient
from aiqatester.knowledge.site_model import SiteModel
from aiqatester.llm.prompt_library import get_prompt
from aiqatester.llm.response_parser import ResponseParser

class TestScriptGenerator:
    """Generates executable test scripts."""
    
    def __init__(self, site_model: SiteModel, llm_client: OpenAIClient):
        """
        Initialize the script generator.
        
        Args:
            site_model: Site model containing website information
            llm_client: LLM client for script generation
        """
        self.site_model = site_model
        self.llm = llm_client
        logger.info("TestScriptGenerator initialized")
        
    async def generate_scripts(self, test_strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate test scripts based on a testing strategy.
        
        Args:
            test_strategy: The testing strategy
            
        Returns:
            List of generated test scripts
        """
        test_cases = test_strategy.get('test_cases', [])
        if not test_cases:
            logger.warning("No test cases found in the strategy")
            return []
        
        logger.info(f"Generating test scripts for {len(test_cases)} test cases")
        
        test_scripts = []
        
        for i, test_case in enumerate(test_cases):
            try:
                # Debug the actual test case format
                logger.debug(f"Test case {i} type: {type(test_case)}")
                
                # Handle different formats of test cases
                if isinstance(test_case, str):
                    logger.warning(f"Converting string test case to dictionary: {test_case}")
                    test_case = {"name": test_case, "description": f"Test for {test_case}", "priority": 3}
                elif not isinstance(test_case, dict):
                    logger.warning(f"Unexpected test case format: {type(test_case)}. Converting to dictionary.")
                    test_case = {"name": f"Test Case {i+1}", "description": str(test_case), "priority": 3}
                
                # Generate test script for the test case
                test_script = await self._generate_test_script(test_case)
                
                # Generate assertions for the script
                assertions = await self._generate_assertions(test_script)
                test_script['assertions'] = assertions
                
                # Identify data requirements
                data_requirements = await self._identify_data_requirements(test_script)
                test_script['data_requirements'] = data_requirements
                
                test_scripts.append(test_script)
                
                logger.info(f"Generated test script for: {test_case.get('name', 'Unknown test case')}")
                
            except Exception as e:
                test_case_name = test_case.get('name', str(test_case)) if isinstance(test_case, dict) else str(test_case)
                logger.error(f"Error generating test script for {test_case_name}: {e}")
        
        return test_scripts
    
    async def _generate_test_script(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a test script for a test case.
        
        Args:
            test_case: The test case to generate a script for
            
        Returns:
            Generated test script
        """
        # Extract relevant page information
        pages_info = ""
        for url, page in self.site_model.pages.items():
            pages_info += f"- {page.title or 'Untitled'} ({url})\n"
            for element_type, elements in page.interactive_elements.items():
                if elements:
                    pages_info += f"  {element_type.capitalize()} elements: {len(elements)}\n"
                    # Include a few examples of elements
                    for i, element in enumerate(elements[:3]):
                        element_info = []
                        if 'id' in element and element['id']:
                            element_info.append(f"id='{element['id']}'")
                        if 'class' in element and element['class']:
                            element_info.append(f"class='{element['class']}'")
                        if 'text' in element and element['text']:
                            element_info.append(f"text='{element['text'][:30]}'")
                        pages_info += f"    - {', '.join(element_info)}\n"
        
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA automation engineer. Generate a detailed, executable test script
        for the given test case. The script should include specific browser actions with exact
        selectors, input values, wait conditions, and verification points.
        
        Your response MUST include a 'steps' array with each step having these fields:
        - step (number)
        - action (string: navigate, click, type, select, wait, etc.)
        - selector (CSS selector or XPath)
        - value (input value if applicable)
        - wait_for (element to wait for after action)
        """
        
        # Convert test case to JSON string for the prompt
        import json
        test_case_json = json.dumps(test_case, indent=2)
        
        prompt = f"""
        Generate a detailed, executable test script for the following test case:
        
        Test Case:
        {test_case_json}
        
        Website Information:
        {pages_info}
        
        The script should include:
        1. Detailed browser actions with exact selectors (CSS or XPath)
        2. Input data values where needed
        3. Explicit wait conditions
        4. Verification points
        
        Include at least 5 detailed steps for this test case.
        
        Format your response as a valid JSON with this structure:
        {{
          "name": "Test name",
          "description": "Test description",
          "priority": priority_number,
          "steps": [
            {{"step": 1, "action": "navigate", "selector": null, "value": "https://example.com", "wait_for": null}},
            {{"step": 2, "action": "click", "selector": "#login-button", "value": null, "wait_for": "#login-form"}},
            ...
          ]
        }}
        """
        
        # Get completion from LLM
        response = await self.llm.get_completion(prompt, system_message)
        
        # For debugging
        logger.debug(f"LLM response for {test_case.get('name', 'Unknown')} (first 200 chars): {response[:200]}")
        
        # Extract structured test script from response
        test_script = ResponseParser.extract_json(response)
        
        # If we couldn't extract a proper script, create a basic one
        if not test_script or not isinstance(test_script, dict):
            logger.warning(f"Failed to parse test script for {test_case.get('name', 'Unknown')}. Creating basic script.")
            test_script = {
                "name": test_case.get("name", "Unknown test case"),
                "description": test_case.get("description", ""),
                "priority": test_case.get("priority", 3),
                "steps": [
                    {"step": 1, "action": "navigate", "selector": None, "value": self.site_model.url, "wait_for": None},
                    {"step": 2, "action": "screenshot", "selector": None, "value": "homepage", "wait_for": None}
                ]
            }
        
        # Ensure we have steps
        if "steps" not in test_script or not test_script["steps"]:
            logger.warning(f"No steps found in generated script for {test_case.get('name', 'Unknown')}. Adding default steps.")
            test_script["steps"] = [
                {"step": 1, "action": "navigate", "selector": None, "value": self.site_model.url, "wait_for": None},
                {"step": 2, "action": "screenshot", "selector": None, "value": "homepage", "wait_for": None}
            ]
        
        # Ensure the script has the test case information
        test_script["name"] = test_case.get("name", test_script.get("name", "Unknown test case"))
        test_script["description"] = test_case.get("description", test_script.get("description", ""))
        test_script["priority"] = test_case.get("priority", test_script.get("priority", 3))
        
        return test_script
    
    async def _generate_assertions(self, test_script: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate assertions for a test script.
        
        Args:
            test_script: The test script to generate assertions for
            
        Returns:
            List of assertions
        """
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA automation engineer. Generate verification assertions for the given
        test script. The assertions should validate that each step of the test works correctly
        and that the expected results are achieved.
        """
        
        # Convert test script to JSON string for the prompt
        import json
        script_json = json.dumps(test_script, indent=2)
        
        prompt = f"""
        Generate verification assertions for the following test script:
        
        Test Script:
        {script_json}
        
        For each step or at key verification points, provide:
        1. What should be asserted/verified
        2. The selector or element to check
        3. The expected value or condition
        4. When the assertion should be performed (after which step)
        
        Format the response as a JSON array of assertion objects.
        """
        
        # Get completion from LLM
        response = await self.llm.get_completion(prompt, system_message)
        
        # Extract assertions from response
        assertions_data = ResponseParser.extract_json(response)
        
        if not assertions_data:
            # Create basic assertions if extraction failed
            assertions_data = []
            
            # Add a basic assertion for each step with a selector
            for i, step in enumerate(test_script.get("steps", [])):
                if step.get("selector"):
                    assertion = {
                        "id": f"assertion_{i + 1}",
                        "type": "element_exists",
                        "element": step.get("selector"),
                        "expected": True,
                        "description": f"Verify element exists after step {i + 1}"
                    }
                    assertions_data.append(assertion)
                
                # Add page assertions for navigation steps
                if step.get("action") == "navigate" and step.get("value"):
                    assertion = {
                        "id": f"assertion_url_{i + 1}",
                        "type": "page_url",
                        "element": None,
                        "expected": step.get("value"),
                        "description": f"Verify URL after navigation in step {i + 1}"
                    }
                    assertions_data.append(assertion)
        
        # Ensure assertions is a list
        if not isinstance(assertions_data, list):
            if isinstance(assertions_data, dict) and "assertions" in assertions_data:
                assertions_data = assertions_data["assertions"]
            else:
                assertions_data = [assertions_data]
        
        return assertions_data
    
    async def _identify_data_requirements(self, test_script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify data requirements for a test script.
        
        Args:
            test_script: The test script to identify data requirements for
            
        Returns:
            Dictionary of data requirements
        """
        # Initialize data requirements
        data_requirements = {}
        
        # Extract data requirements from steps
        for step in test_script.get("steps", []):
            if step.get("value") and isinstance(step["value"], str) and "{" in step["value"] and "}" in step["value"]:
                # Extract variable from placeholders like {username}
                import re
                vars = re.findall(r'\{([^}]+)\}', step["value"])
                
                for var in vars:
                    data_requirements[var] = None
        
        # If no variables found, check for common input fields
        if not data_requirements:
            for step in test_script.get("steps", []):
                action = step.get("action", "").lower()
                if "type" in action or "fill" in action or "input" in action:
                    selector = step.get("selector", "")
                    
                    # Try to identify the type of input
                    if selector and isinstance(selector, str):
                        if "email" in selector.lower():
                            data_requirements["email"] = "test@example.com"
                        elif "password" in selector.lower():
                            data_requirements["password"] = "TestPassword123!"
                        elif "username" in selector.lower() or "user" in selector.lower():
                            data_requirements["username"] = "testuser"
                        elif "name" in selector.lower():
                            data_requirements["name"] = "Test User"
                        elif "search" in selector.lower():
                            data_requirements["search_query"] = "test search"
        
        return data_requirements