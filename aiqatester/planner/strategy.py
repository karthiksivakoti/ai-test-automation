# ai-test-automation/aiqatester/planner/strategy.py
"""
Test Strategy module for AIQATester.

This module plans testing strategies based on website analysis.
"""

from typing import Dict, List, Optional, Any

from loguru import logger

from aiqatester.knowledge.site_model import SiteModel
from aiqatester.llm.openai_client import OpenAIClient
from aiqatester.llm.prompt_library import get_prompt
from aiqatester.llm.response_parser import ResponseParser

class TestStrategy:
    """Plans testing strategies based on website analysis."""
    
    def __init__(self, site_model: SiteModel, llm_client: OpenAIClient):
        """
        Initialize the test strategy planner.
        
        Args:
            site_model: Site model containing website information
            llm_client: LLM client for strategy planning
        """
        self.site_model = site_model
        self.llm = llm_client
        logger.info("TestStrategy initialized")
        
    async def create_strategy(self) -> Dict[str, Any]:
        """
        Create a general testing strategy.
        
        Returns:
            Dictionary containing the testing strategy
        """
        logger.info(f"Creating testing strategy for {self.site_model.url}")
        
        # Extract site information for the LLM
        site_info = self._extract_site_info()
        
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA strategist with deep understanding of web application testing.
        Create a comprehensive testing strategy based on the provided website information.
        Focus on business-critical flows and high-impact areas.
        """
        
        prompt = f"""
        Create a testing strategy for the following website:
        
        Website URL: {self.site_model.url}
        
        Pages:
        {site_info['pages']}
        
        Business Flows:
        {site_info['flows']}
        
        Interactive Elements:
        {site_info['elements']}
        
        Your strategy should include:
        1. Test objectives
        2. Key areas to test
        3. Test approach
        4. Prioritized test cases
        5. Test data needs
        """
        
        try:
            # Get completion from LLM
            response = await self.llm.get_completion(prompt, system_message)
            
            # Ask for structured output
            structured_prompt = """
            Convert your testing strategy into a structured JSON format with the following fields:
            - objectives: Array of test objectives
            - key_areas: Array of key areas to test
            - approach: Testing approach description
            - test_cases: Array of test case objects, each with:
              - name: Test case name
              - description: Test case description
              - priority: Priority (1-5, with 5 being highest)
              - category: Test category
              - business_flow: Related business flow (if applicable)
            - data_needs: Test data requirements
            """
            
            structured_response = await self.llm.get_completion(structured_prompt)
            
            # Parse the JSON response
            strategy_data = ResponseParser.extract_json(structured_response)
            
            if not strategy_data:
                # Create a basic strategy if parsing failed
                strategy_data = {
                    "objectives": ["Verify core functionality", "Identify critical issues"],
                    "key_areas": ["Business flows", "User interfaces"],
                    "approach": "Manual and automated testing",
                    "test_cases": [],
                    "data_needs": {}
                }
                
                # Try to extract test cases separately
                test_cases = ResponseParser.extract_test_cases(response)
                if test_cases:
                    strategy_data["test_cases"] = test_cases
            
            logger.info(f"Created testing strategy with {len(strategy_data.get('test_cases', []))} test cases")
            
            return strategy_data
            
        except Exception as e:
            logger.error(f"Error creating testing strategy: {e}")
            return {
                "objectives": ["Verify core functionality"],
                "key_areas": ["Business flows"],
                "approach": "Manual testing",
                "test_cases": [],
                "data_needs": {}
            }
    
    async def create_strategy_for_task(self, task: str) -> Dict[str, Any]:
        """
        Create a testing strategy focused on a specific task.
        
        Args:
            task: Task description
            
        Returns:
            Dictionary containing the testing strategy
        """
        logger.info(f"Creating testing strategy for task: {task}")
        
        # Extract site information for the LLM
        site_info = self._extract_site_info()
        
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA strategist with deep understanding of web application testing.
        Create a focused testing strategy for the specified task on the provided website.
        Prioritize test cases that directly address the task requirements.
        """
        
        prompt = f"""
        Create a testing strategy for the following task on this website:
        
        Task: {task}
        
        Website URL: {self.site_model.url}
        
        Pages:
        {site_info['pages']}
        
        Business Flows:
        {site_info['flows']}
        
        Interactive Elements:
        {site_info['elements']}
        
        Your strategy should include:
        1. Test objectives specific to the task
        2. Key areas to test
        3. Test approach
        4. Prioritized test cases
        5. Test data needs
        """
        
        try:
            # Get completion from LLM
            response = await self.llm.get_completion(prompt, system_message)
            
            # Ask for structured output
            structured_prompt = """
            Convert your testing strategy into a structured JSON format with the following fields:
            - objectives: Array of test objectives
            - key_areas: Array of key areas to test
            - approach: Testing approach description
            - test_cases: Array of test case objects, each with:
              - name: Test case name
              - description: Test case description
              - priority: Priority (1-5, with 5 being highest)
              - category: Test category
              - business_flow: Related business flow (if applicable)
            - data_needs: Test data requirements
            """
            
            structured_response = await self.llm.get_completion(structured_prompt)
            
            # Parse the JSON response
            strategy_data = ResponseParser.extract_json(structured_response)
            
            if not strategy_data:
                # Create a basic strategy if parsing failed
                strategy_data = {
                    "objectives": [f"Verify {task}"],
                    "key_areas": ["Task-specific functionality"],
                    "approach": "Manual and automated testing",
                    "test_cases": [],
                    "data_needs": {}
                }
                
                # Try to extract test cases separately
                test_cases = ResponseParser.extract_test_cases(response)
                if test_cases:
                    strategy_data["test_cases"] = test_cases
            
            logger.info(f"Created testing strategy for task with {len(strategy_data.get('test_cases', []))} test cases")
            
            return strategy_data
            
        except Exception as e:
            logger.error(f"Error creating testing strategy for task: {e}")
            return {
                "objectives": [f"Verify {task}"],
                "key_areas": ["Task-specific functionality"],
                "approach": "Manual testing",
                "test_cases": [],
                "data_needs": {}
            }
    
    def _extract_site_info(self) -> Dict[str, str]:
        """
        Extract site information for LLM input.
        
        Returns:
            Dictionary containing formatted site information
        """
        # Extract pages information
        pages_info = ""
        for url, page in self.site_model.pages.items():
            pages_info += f"- {page.title or 'Untitled'} ({url})\n"
        
        # Extract business flows information
        flows_info = ""
        for i, flow in enumerate(self.site_model.business_flows):
            flows_info += f"- {flow.get('name', f'Flow {i+1}')}: {flow.get('description', 'No description')}\n"
        
        # Extract interactive elements information
        elements_info = ""
        element_counts = self.site_model.get_interactive_element_count()
        for element_type, count in element_counts.items():
            elements_info += f"- {element_type.capitalize()}: {count}\n"
        
        return {
            "pages": pages_info,
            "flows": flows_info,
            "elements": elements_info
        }