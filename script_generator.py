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
        """Generate test scripts based on a testing strategy."""
        test_cases = test_strategy.get('test_cases', [])
        if not test_cases:
            logger.warning("No test cases found in the strategy")
            return []
        
        logger.info(f"Generating test scripts for {len(test_cases)} test cases")
        test_scripts = []
        
        for test_case in test_cases:
            try:
                # Check if test_case is a string and convert it to dict if needed
                if isinstance(test_case, str):
                    test_case_name = test_case
                    test_case = {"name": test_case_name, "description": test_case_name}
                    logger.warning(f"Converting string test case to dictionary: {test_case_name}")
                
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
                # Safely get name without assuming dictionary structure
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
        # Extract detailed website information for better LLM context
        detailed_site_info = self._extract_detailed_site_info()
        
        # Create a comprehensive prompt for the LLM that includes detailed element information
        system_message = """
        You are an expert QA automation engineer specializing in web application testing.
        Your task is to generate executable browser automation scripts for testing web applications.
        
        Each test script must include concrete steps that interact with real elements on the page.
        Every step must specify:
        1. The exact action to perform (navigate, click, type, wait, etc.)
        2. The precise selector to target (CSS selector or XPath)
        3. Any values to input (for form fields)
        4. Elements to wait for after the action completes
        
        Your script must be executable by a browser automation framework.
        """
        
        # Create detailed user prompt with emphasis on practical executable steps
        prompt = f"""
        I need to create an automated test script for the following test case:
        
        TEST CASE: {test_case.get('name', 'Unnamed Test')}
        DESCRIPTION: {test_case.get('description', 'No description provided')}
        
        WEBSITE DETAILS:
        {detailed_site_info}
        
        Create a concrete, executable test script with specific steps that:
        1. Uses the actual UI elements found on the pages
        2. Includes precise selectors targeting real elements
        3. Contains at least 5-8 detailed steps that thoroughly test the functionality
        4. Specifies any data inputs needed (usernames, passwords, search terms, etc.)
        5. Includes explicit wait conditions where appropriate
        
        The output must be a valid JSON object with this structure:
        {{
          "name": "Test name",
          "description": "Test description",
          "priority": priority_number,
          "steps": [
            {{
              "step": 1,
              "action": "navigate",
              "selector": null,
              "value": "https://example.com",
              "wait_for": null
            }},
            {{
              "step": 2,
              "action": "click",
              "selector": "#login-button",
              "value": null,
              "wait_for": "#login-form"
            }},
            ... more steps ...
          ]
        }}
        
        Make sure to include steps for:
        - Initial navigation to the appropriate URL
        - All interactions required to complete the test case
        - Verification points where appropriate
        - Taking screenshots at key points
        
        Use these action types:
        - "navigate": Go to a URL
        - "click": Click on an element
        - "type": Enter text into a field
        - "select": Select an option from a dropdown
        - "wait": Wait for a specific time (milliseconds)
        - "screenshot": Capture a screenshot
        
        Each selector must target actual elements found on the page.
        """
        
        # Get completion from LLM
        response = await self.llm.get_completion(prompt, system_message)
        
        # Try to extract the JSON script from the response
        test_script = ResponseParser.extract_json(response)
        
        # If extraction failed or no steps were defined, try one more time with a more directive prompt
        if not test_script or "steps" not in test_script or not test_script["steps"]:
            logger.warning(f"Initial script generation failed for {test_case.get('name')}. Trying again with more directive prompt.")
            
            # More directive prompt focused specifically on generating executable steps
            directive_prompt = f"""
            The previous response didn't contain valid executable steps.
            
            Please generate ONLY a JSON object containing concrete test steps for:
            TEST CASE: {test_case.get('name', 'Unnamed Test')}
            
            The steps must:
            1. Be executable by a browser automation framework
            2. Include precise CSS selectors or XPath expressions
            3. Use actual UI elements from the website
            
            I need at least 5 detailed steps in this exact JSON format:
            {{
              "steps": [
                {{"step": 1, "action": "navigate", "selector": null, "value": "https://example.com", "wait_for": null}},
                {{"step": 2, "action": "click", "selector": "a.login-link", "value": null, "wait_for": "form.login"}},
                ...more steps...
              ]
            }}
            
            Only provide the JSON object, nothing else.
            """
            
            # Try again
            retry_response = await self.llm.get_completion(directive_prompt)
            test_script_retry = ResponseParser.extract_json(retry_response)
            
            # If we got steps in the retry, use those
            if test_script_retry and "steps" in test_script_retry and test_script_retry["steps"]:
                # If we didn't get a full test script but just steps, merge with original test case info
                if not test_script:
                    test_script = {
                        "name": test_case.get("name", "Unknown test case"),
                        "description": test_case.get("description", ""),
                        "priority": test_case.get("priority", 3),
                        "steps": test_script_retry["steps"]
                    }
                else:
                    test_script["steps"] = test_script_retry["steps"]
                
                logger.info(f"Successfully generated steps on retry for: {test_case.get('name')}")
            else:
                # If we still failed, create a minimal script structure
                logger.error(f"Failed to generate executable steps for {test_case.get('name')} after retry")
                test_script = {
                    "name": test_case.get("name", "Unknown test case"),
                    "description": test_case.get("description", ""),
                    "priority": test_case.get("priority", 3),
                    "steps": [] # Empty steps array - this will cause the test to be skipped
                }
        
        # Ensure the script has the test case information
        if test_script:
            test_script["name"] = test_case.get("name", test_script.get("name", "Unknown test case"))
            test_script["description"] = test_case.get("description", test_script.get("description", ""))
            test_script["priority"] = test_case.get("priority", test_script.get("priority", 3))
        
        # Log the test script generation result
        steps_count = len(test_script.get("steps", [])) if test_script else 0
        if steps_count > 0:
            logger.info(f"Generated {steps_count} steps for test: {test_case.get('name')}")
        else:
            logger.warning(f"No steps were generated for test: {test_case.get('name')}")
        
        return test_script
    
    def _extract_detailed_site_info(self) -> str:
        """
        Extract detailed website information including elements for better LLM context.
        
        Returns:
            Formatted string with detailed site info
        """
        site_info = f"Base URL: {self.site_model.url}\n\n"
        site_info += "PAGES DETECTED:\n"
        
        for url, page in self.site_model.pages.items():
            site_info += f"- PAGE: {page.title or 'Untitled'} ({url})\n"
            
            # Add interactive elements with detailed information
            for element_type, elements in page.interactive_elements.items():
                if not elements:
                    continue
                    
                site_info += f"  {element_type.capitalize()} elements ({len(elements)}):\n"
                
                # Include detailed information about each element (limited to avoid prompt size issues)
                for i, element in enumerate(elements[:10]):
                    element_info = []
                    
                    if 'id' in element and element['id']:
                        element_info.append(f"id='{element['id']}'")
                    
                    if 'class' in element and element['class']:
                        element_info.append(f"class='{element['class']}'")
                    
                    if 'text' in element and element['text']:
                        # Truncate long text
                        text = element['text'][:30] + ("..." if len(element['text']) > 30 else "")
                        element_info.append(f"text='{text}'")
                    
                    if 'href' in element and element['href']:
                        # Truncate long URLs
                        href = element['href'][:30] + ("..." if len(element['href']) > 30 else "")
                        element_info.append(f"href='{href}'")
                    
                    if 'name' in element and element['name']:
                        element_info.append(f"name='{element['name']}'")
                    
                    if 'type' in element and element['type']:
                        element_info.append(f"type='{element['type']}'")
                    
                    # Combine all attributes
                    attributes = ", ".join(element_info)
                    site_info += f"    - Element {i+1}: {attributes}\n"
                
                # Indicate if there are more elements
                if len(elements) > 10:
                    site_info += f"    - ... and {len(elements) - 10} more {element_type} elements\n"
            
            # Add a separator between pages
            site_info += "\n"
        
        # Add information about detected business flows
        if self.site_model.business_flows:
            site_info += "BUSINESS FLOWS DETECTED:\n"
            for i, flow in enumerate(self.site_model.business_flows):
                site_info += f"- Flow {i+1}: {flow.get('name', 'Unnamed Flow')}\n"
                site_info += f"  Description: {flow.get('description', 'No description')}\n"
                
                # Add flow steps if available
                if 'steps' in flow:
                    site_info += "  Steps:\n"
                    for j, step in enumerate(flow['steps']):
                        site_info += f"    {j+1}. {step.get('description', 'No description')}\n"
                
                site_info += "\n"
        
        return site_info
    
    async def _generate_assertions(self, test_script: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate assertions for a test script.
        
        Args:
            test_script: The test script to generate assertions for
            
        Returns:
            List of assertions
        """
        # If there are no steps, we can't generate meaningful assertions
        if not test_script or not test_script.get("steps"):
            return []
            
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA automation engineer. Generate verification assertions for the given
        test script. Each assertion should verify a specific aspect of the application's behavior
        after executing certain steps in the test.
        
        Assertions should be specific, measurable, and directly tied to the test steps.
        """
        
        # Convert test script to JSON string for the prompt
        import json
        script_json = json.dumps(test_script, indent=2)
        
        prompt = f"""
        Generate verification assertions for the following test script:
        
        Test Script:
        {script_json}
        
        For each key verification point in the test, create an assertion that:
        1. Verifies a specific element or page state
        2. Specifies the exact element to check using a CSS selector
        3. Defines the expected value or condition
        4. Indicates when the assertion should be performed (after which step)
        
        The assertions should follow this structure:
        {{
          "id": "assertion_id",
          "type": "assertion_type",
          "element": "CSS selector or XPath",
          "expected": expected_value,
          "description": "Description of what is being verified"
        }}
        
        Common assertion types include:
        - "element_exists": Check if an element exists
        - "element_visible": Check if an element is visible
        - "element_text": Check element text content
        - "element_value": Check input field value
        - "page_url": Check the current page URL
        - "page_title": Check the page title
        
        Return a JSON array of assertion objects.
        """
        
        # Get completion from LLM
        response = await self.llm.get_completion(prompt, system_message)
        
        # Extract assertions from response
        assertions_data = ResponseParser.extract_json(response)
        
        # Process the response to ensure it's properly structured
        if assertions_data:
            # If it's already a list, use it
            if isinstance(assertions_data, list):
                return assertions_data
            
            # If it's a dictionary with an "assertions" key, extract that
            if isinstance(assertions_data, dict) and 'assertions' in assertions_data:
                return assertions_data['assertions']
        
        # If we couldn't extract assertions, generate basic ones based on the test steps
        logger.warning(f"Failed to generate assertions for {test_script.get('name')}. Creating basic assertions.")
        
        basic_assertions = []
        for i, step in enumerate(test_script.get("steps", [])):
            # Skip steps that don't have selectors or appropriate actions for assertions
            if not step.get("selector") or step.get("action") in ["screenshot", "wait"]:
                continue
                
            # Create a basic assertion based on the step type
            if step.get("action") == "click":
                basic_assertions.append({
                    "id": f"assertion_{i + 1}",
                    "type": "element_exists",
                    "element": step.get("wait_for") or step.get("selector"),
                    "expected": True,
                    "description": f"Verify element exists after clicking in step {i + 1}"
                })
            elif step.get("action") == "type":
                basic_assertions.append({
                    "id": f"assertion_value_{i + 1}",
                    "type": "element_value",
                    "element": step.get("selector"),
                    "expected": step.get("value"),
                    "description": f"Verify input value after typing in step {i + 1}"
                })
            elif step.get("action") == "navigate":
                basic_assertions.append({
                    "id": f"assertion_url_{i + 1}",
                    "type": "page_url",
                    "element": None,
                    "expected": step.get("value"),
                    "description": f"Verify URL after navigation in step {i + 1}"
                })
        
        return basic_assertions
    
    async def _identify_data_requirements(self, test_script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify data requirements for a test script.
        
        Args:
            test_script: The test script to identify data requirements for
            
        Returns:
            Dictionary of data requirements
        """
        # If there are no steps, there can't be data requirements
        if not test_script or not test_script.get("steps"):
            return {}
            
        # Initialize data requirements
        data_requirements = {}
        
        # Extract data requirements from steps
        for step in test_script.get("steps", []):
            if step.get("value") and "{" in str(step["value"]) and "}" in str(step["value"]):
                # Extract variable from placeholders like {username}
                import re
                vars = re.findall(r'\{([^}]+)\}', str(step["value"]))
                
                for var in vars:
                    # Add the variable to requirements but don't provide a default value yet
                    data_requirements[var] = None
        
        # If no explicit variables were found, look for implicit data needs based on step types
        if not data_requirements:
            # Ask LLM to identify data requirements based on the test script
            system_message = """
            You are an expert QA data analyst. Identify the test data requirements for the given test script.
            Focus on what data would be needed to execute this test script successfully.
            """
            
            import json
            script_json = json.dumps(test_script, indent=2)
            
            prompt = f"""
            Analyze this test script and identify what test data would be required to execute it:
            
            {script_json}
            
            For each data requirement, specify:
            1. A descriptive name for the data item (e.g., username, password, search_term)
            2. A sample value that would be appropriate for testing
            
            Return your analysis as a JSON object where keys are data item names and values are sample values.
            """
            
            try:
                # Get completion from LLM
                response = await self.llm.get_completion(prompt, system_message)
                
                # Try to extract the data requirements
                llm_data_requirements = ResponseParser.extract_json(response)
                
                # If we got valid data requirements, use them
                if llm_data_requirements and isinstance(llm_data_requirements, dict):
                    data_requirements.update(llm_data_requirements)
            except Exception as e:
                logger.error(f"Error identifying data requirements via LLM: {e}")
                
                # Fall back to basic inference from steps
                for step in test_script.get("steps", []):
                    action = step.get("action", "").lower()
                    selector = step.get("selector", "").lower()
                    value = step.get("value")
                    
                    # Only analyze type actions with values
                    if action == "type" and value:
                        # Try to identify the type of input based on the selector
                        if "email" in selector:
                            data_requirements["email"] = "test@example.com"
                        elif "password" in selector:
                            data_requirements["password"] = "TestPassword123!"
                        elif "user" in selector or "name" in selector:
                            data_requirements["username"] = "testuser"
                        elif "search" in selector or "query" in selector:
                            data_requirements["search_query"] = "test search"
        
        return data_requirements