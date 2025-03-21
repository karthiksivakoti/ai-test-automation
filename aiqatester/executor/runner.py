# ai-test-automation/aiqatester/executor/runner.py
"""
Test Runner module for AIQATester.

This module executes test scripts and captures results.
"""

from typing import Dict, List, Any
import time
import asyncio

from loguru import logger

from aiqatester.browser.controller import BrowserController
from aiqatester.browser.actions import BrowserActions

class TestRunner:
    """Executes test scripts and captures results."""
    
    def __init__(self, browser_controller: BrowserController):
        """
        Initialize the test runner.
        
        Args:
            browser_controller: Browser controller instance
        """
        self.browser = browser_controller
        self.browser_actions = BrowserActions(browser_controller)
        logger.info("TestRunner initialized")
        
    async def run_test(self, test_script: Dict[str, Any], test_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a test script with the provided test data.
        
        Args:
            test_script: The test script to run
            test_data: Test data to use
            
        Returns:
            Test results
        """
        test_name = test_script.get("name", "Unknown test")
        logger.info(f"Running test script: {test_name}")
        
        # Initialize results
        results = {
            "name": test_name,
            "description": test_script.get("description", ""),
            "status": "not_started",
            "steps": [],
            "assertions": [],
            "start_time": time.time(),
            "end_time": None,
            "duration": 0,
            "screenshots": []
        }
        
        # If no test data is provided, use empty dict
        if test_data is None:
            test_data = {}
        
        # Execute test steps
        try:
            # Execute each step
            steps = test_script.get("steps", [])
            
            if not steps:
                logger.warning(f"No steps found in test script: {test_name}")
                results["status"] = "skipped"
                results["end_time"] = time.time()
                results["duration"] = results["end_time"] - results["start_time"]
                return results
            
            for i, step in enumerate(steps):
                # Skip if not a dict
                if not isinstance(step, dict):
                    continue
                
                step_result = await self._execute_step(step, i + 1, test_data)
                results["steps"].append(step_result)
                
                # If step failed, stop test execution
                if step_result["status"] == "failed":
                    logger.error(f"Step {i + 1} failed in test: {test_name}")
                    results["status"] = "failed"
                    break
            
            # If all steps passed, check assertions
            if results["status"] != "failed":
                assertions = test_script.get("assertions", [])
                for assertion in assertions:
                    assertion_result = await self._check_assertion(assertion)
                    results["assertions"].append(assertion_result)
                    
                    # If assertion failed, test fails
                    if assertion_result["status"] == "failed":
                        logger.error(f"Assertion failed in test: {test_name}")
                        results["status"] = "failed"
                        break
                
                # If status is still not set, test passed
                if results["status"] == "not_started":
                    results["status"] = "passed"
                    logger.info(f"Test passed: {test_name}")
            
            # Take final screenshot
            screenshot = await self.browser.take_screenshot(f"test_{test_name.replace(' ', '_')}_final")
            results["screenshots"].append(screenshot)
            
        except Exception as e:
            logger.error(f"Error running test script {test_name}: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            
            # Take error screenshot
            try:
                screenshot = await self.browser.take_screenshot(f"test_{test_name.replace(' ', '_')}_error")
                results["screenshots"].append(screenshot)
            except Exception as screenshot_error:
                logger.error(f"Failed to take error screenshot: {screenshot_error}")
        
        # Calculate duration
        results["end_time"] = time.time()
        results["duration"] = results["end_time"] - results["start_time"]
        
        return results
        
    async def run_test_suite(self, test_scripts: List[Dict[str, Any]], test_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run a suite of test scripts.
        
        Args:
            test_scripts: List of test scripts to run
            test_data: Test data to use
            
        Returns:
            Test suite results
        """
        logger.info(f"Running test suite with {len(test_scripts)} test scripts")
        
        # Initialize suite results
        suite_results = {
            "total": len(test_scripts),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "error": 0,
            "start_time": time.time(),
            "end_time": None,
            "duration": 0,
            "results": []
        }
        
        # If no test data is provided, generate some
        if test_data is None:
            from aiqatester.data.generator import DataGenerator
            data_generator = DataGenerator()
            test_data = data_generator.generate_default_data()
        
        # Run each test script
        for test_script in test_scripts:
            try:
                test_result = await self.run_test(test_script, test_data)
                suite_results["results"].append(test_result)
                
                # Update counts
                if test_result["status"] == "passed":
                    suite_results["passed"] += 1
                elif test_result["status"] == "failed":
                    suite_results["failed"] += 1
                elif test_result["status"] == "skipped":
                    suite_results["skipped"] += 1
                elif test_result["status"] == "error":
                    suite_results["error"] += 1
                
                # Short delay between tests
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error running test script: {e}")
                suite_results["error"] += 1
        
        # Calculate duration
        suite_results["end_time"] = time.time()
        suite_results["duration"] = suite_results["end_time"] - suite_results["start_time"]
        
        logger.info(f"Test suite completed: {suite_results['passed']} passed, {suite_results['failed']} failed, {suite_results['skipped']} skipped, {suite_results['error']} errors")
        
        return suite_results
    
    async def _execute_step(self, step: Dict[str, Any], step_number: int, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a test step.
        
        Args:
            step: Test step to execute
            step_number: Step number
            test_data: Test data to use
            
        Returns:
            Step execution results
        """
        logger.info(f"Executing step {step_number}: {step.get('action', '')}")
        
        # Initialize step result
        step_result = {
            "step": step_number,
            "action": step.get("action", ""),
            "status": "not_started",
            "start_time": time.time(),
            "end_time": None,
            "duration": 0,
            "screenshot": None
        }
        
        try:
            # Extract step information
            action = step.get("action", "").lower()
            selector = step.get("selector", "")
            value = step.get("value", "")
            wait_for = step.get("wait_for", "")
            
            # Replace data placeholders
            if value and isinstance(value, str):
                import re
                for match in re.finditer(r'\{([^}]+)\}', value):
                    placeholder = match.group(1)
                    if placeholder in test_data:
                        value = value.replace(f"{{{placeholder}}}", str(test_data[placeholder]))
            
            # Execute action based on type
            success = False
            
            if "navigate" in action or "go to" in action:
                # Navigate to URL
                if not value and selector:
                    value = selector  # Use selector as URL if value is not provided
                
                await self.browser.navigate(value)
                success = True
                
            elif "click" in action:
                # Click element
                success = await self.browser.click(selector)
                
            elif "type" in action or "fill" in action or "input" in action:
                # Type text
                success = await self.browser.type_text(selector, value)
                
            elif "select" in action:
                # Select option
                success = await self.browser.select_option(selector, value=value)
                
            elif "wait" in action:
                # Wait for element or timeout
                if selector:
                    success = await self.browser.wait_for_selector(selector)
                else:
                    # Wait for a fixed time
                    timeout = int(value) if value and value.isdigit() else 1000
                    await asyncio.sleep(timeout / 1000)  # Convert to seconds
                    success = True
                    
            elif "screenshot" in action:
                # Take screenshot
                screenshot_name = value or f"step_{step_number}"
                screenshot = await self.browser.take_screenshot(screenshot_name)
                step_result["screenshot"] = screenshot
                success = True
                
            else:
                # Unknown action
                logger.warning(f"Unknown action in step {step_number}: {action}")
                success = False
            
            # Wait for additional element if specified
            if wait_for:
                await self.browser.wait_for_selector(wait_for)
            
            # Update step result
            step_result["status"] = "passed" if success else "failed"
            
            # Take screenshot
            try:
                screenshot = await self.browser.take_screenshot(f"step_{step_number}")
                step_result["screenshot"] = screenshot
            except Exception as screenshot_error:
                logger.warning(f"Failed to take step screenshot: {screenshot_error}")
            
        except Exception as e:
            logger.error(f"Error executing step {step_number}: {e}")
            step_result["status"] = "failed"
            step_result["error"] = str(e)
            
            # Take error screenshot
            try:
                screenshot = await self.browser.take_screenshot(f"step_{step_number}_error")
                step_result["screenshot"] = screenshot
            except Exception as screenshot_error:
                logger.warning(f"Failed to take error screenshot: {screenshot_error}")
        
        # Calculate duration
        step_result["end_time"] = time.time()
        step_result["duration"] = step_result["end_time"] - step_result["start_time"]
        
        return step_result
    
    async def _check_assertion(self, assertion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check an assertion.
        
        Args:
            assertion: Assertion to check
            
        Returns:
            Assertion check results
        """
        assertion_id = assertion.get("id", "unknown")
        assertion_type = assertion.get("type", "")
        element = assertion.get("element", "")
        expected = assertion.get("expected", "")
        
        logger.info(f"Checking assertion {assertion_id}: {assertion_type}")
        
        # Initialize assertion result
        assertion_result = {
            "id": assertion_id,
            "type": assertion_type,
            "description": assertion.get("description", ""),
            "status": "not_started",
            "start_time": time.time(),
            "end_time": None,
            "duration": 0,
            "actual": None
        }
        
        try:
            actual = None
            
            # Check assertion based on type
            if assertion_type == "element_exists":
                # Check if element exists
                element_handle = await self.browser.get_element_by_selector(element)
                actual = element_handle is not None
                assertion_result["status"] = "passed" if actual == expected else "failed"
                
            elif assertion_type == "element_visible":
                # Check if element is visible
                visible = await self.browser.page.is_visible(element)
                actual = visible
                assertion_result["status"] = "passed" if actual == expected else "failed"
                
            elif assertion_type == "element_not_visible":
                # Check if element is not visible
                visible = await self.browser.page.is_visible(element)
                actual = not visible
                assertion_result["status"] = "passed" if actual == expected else "failed"
                
            elif assertion_type == "element_text":
                # Check element text
                text = await self.browser.get_element_text(element)
                actual = text
                
                # Compare based on expected type
                if isinstance(expected, str):
                    # Exact match
                    assertion_result["status"] = "passed" if actual == expected else "failed"
                elif isinstance(expected, dict) and "contains" in expected:
                    # Contains match
                    contains_text = expected["contains"]
                    assertion_result["status"] = "passed" if contains_text in actual else "failed"
                else:
                    # Default to exact match
                    assertion_result["status"] = "passed" if str(actual) == str(expected) else "failed"
                
            elif assertion_type == "element_value":
                # Check input value
                value = await self.browser.page.input_value(element)
                actual = value
                assertion_result["status"] = "passed" if actual == expected else "failed"
                
            elif assertion_type == "element_attribute":
                # Check element attribute
                if isinstance(expected, dict) and "name" in expected and "value" in expected:
                    attribute_name = expected["name"]
                    attribute_value = expected["value"]
                    
                    element_handle = await self.browser.get_element_by_selector(element)
                    if element_handle:
                        attribute = await element_handle.get_attribute(attribute_name)
                        actual = attribute
                        assertion_result["status"] = "passed" if actual == attribute_value else "failed"
                    else:
                        actual = None
                        assertion_result["status"] = "failed"
                else:
                    actual = None
                    assertion_result["status"] = "failed"
                    
            elif assertion_type == "page_url":
                # Check page URL
                url = self.browser.page.url
                actual = url
                
                # Compare based on expected type
                if isinstance(expected, str):
                    # Exact match or contains match
                    if expected.startswith("contains:"):
                        contains_url = expected.replace("contains:", "").strip()
                        assertion_result["status"] = "passed" if contains_url in actual else "failed"
                    else:
                        assertion_result["status"] = "passed" if actual == expected else "failed"
                else:
                    # Default to exact match
                    assertion_result["status"] = "passed" if str(actual) == str(expected) else "failed"
                
            elif assertion_type == "page_title":
                # Check page title
                title = await self.browser.page.title()
                actual = title
                assertion_result["status"] = "passed" if actual == expected else "failed"
                
            else:
                # Unknown assertion type
                logger.warning(f"Unknown assertion type: {assertion_type}")
                assertion_result["status"] = "skipped"
            
            # Set actual value
            assertion_result["actual"] = actual
            
        except Exception as e:
            logger.error(f"Error checking assertion {assertion_id}: {e}")
            assertion_result["status"] = "error"
            assertion_result["error"] = str(e)
        
        # Calculate duration
        assertion_result["end_time"] = time.time()
        assertion_result["duration"] = assertion_result["end_time"] - assertion_result["start_time"]
        
        return assertion_result