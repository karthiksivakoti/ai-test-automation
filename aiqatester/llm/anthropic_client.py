# ai-test-automation/aiqatester/llm/anthropic_client.py
"""
Anthropic Client module for AIQATester.

This module provides integration with Anthropic's Claude language models.
"""

import os
import re
from typing import Dict, List, Optional, Any, Union
import json

from loguru import logger
import anthropic

class AnthropicClient:
    """Client for Anthropic's Claude language models."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """
        Initialize the Anthropic client.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY environment variable)
            model: Model to use
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
            
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)
        logger.info(f"AnthropicClient initialized with model {model}")
        
    async def get_completion(self, prompt: str, system_message: Optional[str] = None) -> str:
        """
        Get a completion from the model.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            
        Returns:
            Model completion
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_message,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error getting completion: {e}")
            raise
            
    async def analyze_website(self, html_content: str, site_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze website content using the language model.
        
        Args:
            html_content: HTML content of the website
            site_description: Optional site description for context
            
        Returns:
            Analysis results
        """
        system_message = """
        You are an expert QA tester with deep understanding of web applications.
        Analyze the provided HTML content and extract key information about the website's
        purpose, structure, and functionality. Focus on identifying business processes
        and potential test cases.
        """
        
        prompt = "Analyze the following website HTML and identify its purpose, key features, and business functions.\n"
        
        if site_description:
            prompt += f"Site description: {site_description}\n\n"
            
        # Truncate HTML if it's too large
        html_preview = html_content[:5000] + "..." if len(html_content) > 5000 else html_content
        prompt += f"HTML Content:\n{html_preview}"
        
        try:
            response = await self.get_completion(prompt, system_message)
            
            # Try to extract structured information
            structured_prompt = """
            Based on your analysis, provide a structured JSON output with the following fields:
            - site_purpose: The main purpose of the website
            - business_functions: List of main business functions
            - key_features: List of key features
            - user_flows: Potential user flows
            - test_priorities: Areas that should be prioritized for testing
            """
            
            structured_response = await self.get_completion(structured_prompt)
            
            # Try to parse the JSON
            try:
                # Extract JSON if it's wrapped in markdown code blocks
                json_match = re.search(r"```json\n(.+?)\n```", structured_response, re.DOTALL)
                if json_match:
                    structured_response = json_match.group(1)
                    
                structured_data = json.loads(structured_response)
                return structured_data
            except Exception as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                return {"analysis": response}
                
        except Exception as e:
            logger.error(f"Error analyzing website: {e}")
            return {"error": str(e)}
    
    async def generate_test_cases(self, site_model: Dict[str, Any], business_flow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate test cases for a business flow.
        
        Args:
            site_model: Information about the website
            business_flow: Information about the business flow
            
        Returns:
            List of test cases
        """
        system_message = """
        You are an expert QA test engineer. Generate thorough test cases for the given business flow.
        For each test case, provide:
        - name: A descriptive name
        - description: What the test case verifies
        - priority: Priority level (1-5, with 5 being highest)
        - preconditions: What must be true before test execution
        - steps: Detailed test steps
        - expected_results: What should happen if the test passes
        - data_requirements: What test data is needed
        """
        
        # Create a summary of the site model
        site_summary = f"Website: {site_model.get('url', 'Unknown')}\n"
        site_summary += f"Pages: {len(site_model.get('pages', {}))}\n"
        
        # Create a JSON representation of the business flow
        flow_json = json.dumps(business_flow, indent=2)
        
        prompt = f"""
        Generate comprehensive test cases for the following business flow:
        
        {site_summary}
        
        Business Flow:
        {flow_json}
        
        Create at least 3 test cases for this flow, including both happy path and edge cases.
        Make test steps detailed and specific, referencing actual page elements where possible.
        """
        
        try:
            response = await self.get_completion(prompt, system_message)
            
            # Parse the response to extract test cases
            structured_prompt = """
            Format your test cases into a proper JSON array where each test case has the following structure:
            {
              "name": "Test case name",
              "description": "Test case description",
              "priority": priority_number,
              "preconditions": ["precondition1", "precondition2"],
              "steps": [
                {"step": 1, "action": "action description", "element": "element selector if applicable"},
                {"step": 2, "action": "action description", "element": "element selector if applicable"}
              ],
              "expected_results": ["expected result 1", "expected result 2"],
              "data_requirements": {"field1": "value1", "field2": "value2"}
            }
            """
            
            structured_response = await self.get_completion(structured_prompt)
            
            # Try to parse the JSON
            try:
                # Extract JSON if it's wrapped in markdown code blocks
                json_match = re.search(r"```json\n(.+?)\n```", structured_response, re.DOTALL)
                if json_match:
                    structured_response = json_match.group(1)
                    
                test_cases = json.loads(structured_response)
                if not isinstance(test_cases, list):
                    test_cases = [test_cases]
                
                return test_cases
            except Exception as e:
                logger.warning(f"Failed to parse JSON response for test cases: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating test cases: {e}")
            return []