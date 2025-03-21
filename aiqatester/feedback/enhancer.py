# ai-test-automation/aiqatester/feedback/enhancer.py
"""
Test Enhancer module for AIQATester.

This module enhances test scripts based on feedback.
"""

from typing import Dict, List, Any

from loguru import logger

from aiqatester.llm.openai_client import OpenAIClient
from aiqatester.llm.response_parser import ResponseParser

class TestEnhancer:
    """Enhances test scripts based on feedback."""
    
    def __init__(self, llm_client: OpenAIClient):
        """
        Initialize the test enhancer.
        
        Args:
            llm_client: LLM client for test enhancement
        """
        self.llm = llm_client
        logger.info("TestEnhancer initialized")
        
    async def enhance_test_script(self, test_script: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance a test script based on feedback.
        
        Args:
            test_script: Test script to enhance
            feedback: Feedback to use for enhancement
            
        Returns:
            Enhanced test script
        """
        test_name = test_script.get("name", "Unknown test")
        logger.info(f"Enhancing test script: {test_name}")
        
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA automation engineer. Enhance the given test script
        based on the provided feedback. Improve steps, selectors, assertions,
        and error handling to make the test more robust and reliable.
        """
        
        # Convert test script and feedback to JSON strings
        import json
        script_json = json.dumps(test_script, indent=2)
        feedback_json = json.dumps(feedback, indent=2)
        
        prompt = f"""
        Enhance the following test script based on the provided feedback:
        
        Test Script:
        {script_json}
        
        Feedback:
        {feedback_json}
        
        Improve the test script in the following ways:
        1. Fix any issues identified in the feedback
        2. Make selectors more robust
        3. Add appropriate wait conditions
        4. Improve assertions
        5. Add error handling
        6. Any other enhancements to improve reliability
        
        Return the enhanced test script in the same JSON format.
        """
        
        try:
            # Get completion from LLM
            response = await self.llm.get_completion(prompt, system_message)
            
            # Extract JSON from response
            enhanced_script = ResponseParser.extract_json(response)
            
            if not enhanced_script:
                logger.warning(f"Failed to parse enhanced script for test: {test_name}")
                return test_script
            
            logger.info(f"Enhanced test script: {test_name}")
            return enhanced_script
            
        except Exception as e:
            logger.error(f"Error enhancing test script {test_name}: {e}")
            return test_script
    
    async def add_assertions(self, test_script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add assertions to a test script.
        
        Args:
            test_script: Test script to enhance
            
        Returns:
            Enhanced test script with additional assertions
        """
        test_name = test_script.get("name", "Unknown test")
        logger.info(f"Adding assertions to test script: {test_name}")
        
        # Get existing assertions
        existing_assertions = test_script.get("assertions", [])
        
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA automation engineer. Add appropriate assertions
        to the given test script to verify that the test is working correctly.
        """
        
        # Convert test script to JSON string
        import json
        script_json = json.dumps(test_script, indent=2)
        
        prompt = f"""
        Add appropriate assertions to the following test script:
        
        Test Script:
        {script_json}
        
        Current Assertions:
        {json.dumps(existing_assertions, indent=2) if existing_assertions else "No existing assertions."}
        
        For each step or at key verification points, identify:
        1. What should be asserted/verified
        2. The selector or element to check
        3. The expected value or condition
        4. When the assertion should be performed (after which step)
        
        Return new assertions to add in the same format as the existing ones.
        """
        
        try:
            # Get completion from LLM
            response = await self.llm.get_completion(prompt, system_message)
            
            # Extract JSON from response
            new_assertions = ResponseParser.extract_json(response)
            
            if not new_assertions:
                logger.warning(f"Failed to parse new assertions for test: {test_name}")
                return test_script
            
            # Ensure new_assertions is a list
            if not isinstance(new_assertions, list):
                if isinstance(new_assertions, dict) and "assertions" in new_assertions:
                    new_assertions = new_assertions["assertions"]
                else:
                    new_assertions = [new_assertions]
            
            # Add new assertions to test script
            all_assertions = existing_assertions + new_assertions
            
            # Remove duplicates based on element and type
            unique_assertions = []
            seen = set()
            for assertion in all_assertions:
                key = f"{assertion.get('element', '')}-{assertion.get('type', '')}"
                if key not in seen:
                    seen.add(key)
                    unique_assertions.append(assertion)
            
            # Update test script with unique assertions
            test_script["assertions"] = unique_assertions
            
            logger.info(f"Added {len(new_assertions)} assertions to test script: {test_name}")
            return test_script
            
        except Exception as e:
            logger.error(f"Error adding assertions to test script {test_name}: {e}")
            return test_script
    
    async def improve_selectors(self, test_script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Improve selectors in a test script.
        
        Args:
            test_script: Test script to enhance
            
        Returns:
            Enhanced test script with improved selectors
        """
        test_name = test_script.get("name", "Unknown test")
        logger.info(f"Improving selectors in test script: {test_name}")
        
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA automation engineer. Improve the selectors in the given
        test script to make them more robust and reliable. Use best practices for
        selecting elements, such as:
        1. Prefer IDs over other selectors
        2. Use data-testid attributes if available
        3. Use combinations of attributes for greater specificity
        4. Avoid using indexes where possible
        5. Prefer content-based selectors over structural ones
        """
        
        # Convert test script to JSON string
        import json
        script_json = json.dumps(test_script, indent=2)
        
        prompt = f"""
        Improve the selectors in the following test script:
        
        Test Script:
        {script_json}
        
        For each step that uses a selector, suggest a more robust alternative.
        Return the improved test script in the same JSON format.
        """
        
        try:
            # Get completion from LLM
            response = await self.llm.get_completion(prompt, system_message)
            
            # Extract JSON from response
            improved_script = ResponseParser.extract_json(response)
            
            if not improved_script:
                logger.warning(f"Failed to parse improved script for test: {test_name}")
                return test_script
            
            logger.info(f"Improved selectors in test script: {test_name}")
            return improved_script
            
        except Exception as e:
            logger.error(f"Error improving selectors in test script {test_name}: {e}")
            return test_script