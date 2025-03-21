# ai-test-automation/aiqatester/analyzer/business_analyzer.py
"""
Business Logic Analyzer module for AIQATester.

This module identifies and analyzes business processes and use cases in websites.
"""

from typing import Dict, List, Optional, Any

from loguru import logger

from aiqatester.browser.controller import BrowserController
from aiqatester.knowledge.site_model import SiteModel
from aiqatester.llm.openai_client import OpenAIClient

class BusinessAnalyzer:
    """Analyzes business logic and processes in websites."""
    
    def __init__(self, browser_controller: BrowserController, llm_client: OpenAIClient):
        """
        Initialize the business logic analyzer.
        
        Args:
            browser_controller: Browser controller instance
            llm_client: LLM client for business logic understanding
        """
        self.browser = browser_controller
        self.llm = llm_client
        logger.info("BusinessAnalyzer initialized")
        
    async def identify_business_flows(self, site_model: SiteModel) -> Dict[str, Any]:
        """
        Identify business flows and use cases in the website.
        
        Args:
            site_model: Site model containing website information
            
        Returns:
            Dictionary of identified business flows
        """
        business_flows = []
        
        # Extract site information for analysis
        site_info = self._extract_site_info(site_model)
        
        # Use LLM to identify business flows
        system_message = """
        You are an expert QA tester with deep understanding of web applications.
        Analyze the provided website information and identify key business flows that should be tested.
        For each business flow, provide:
        1. Name: A descriptive name for the flow
        2. Description: What the flow accomplishes
        3. Priority: A number from 1-5, with 5 being highest priority
        4. Starting point: Where the flow begins
        5. Steps: Key steps in the flow
        6. Success criteria: How to determine if the flow works correctly
        """
        
        prompt = f"""
        Analyze the following website information and identify key business flows:
        
        Site URL: {site_model.url}
        
        Pages:
        {site_info['pages']}
        
        Interactive Elements:
        {site_info['elements']}
        
        Identify 3-5 key business flows that should be tested on this website.
        """
        
        try:
            # Get completion from LLM
            response = await self.llm.get_completion(prompt, system_message)
            
            # Parse LLM response to extract business flows
            parsed_flows = await self._parse_business_flows(response)
            business_flows.extend(parsed_flows)
            
            logger.info(f"Identified {len(business_flows)} business flows")
            
        except Exception as e:
            logger.error(f"Error identifying business flows: {e}")
        
        return {"flows": business_flows}
    
    def _extract_site_info(self, site_model: SiteModel) -> Dict[str, str]:
        """
        Extract site information for LLM analysis.
        
        Args:
            site_model: Site model
            
        Returns:
            Dictionary of site information
        """
        pages_info = ""
        for url, page in site_model.pages.items():
            pages_info += f"Page: {page.title} ({url})\n"
            pages_info += f"Content: {page.content_summary}\n\n"
        
        elements_info = ""
        for url, page in site_model.pages.items():
            elements_info += f"Page: {page.title} ({url})\n"
            
            for element_type, elements in page.interactive_elements.items():
                elements_info += f"  {element_type.capitalize()}:\n"
                
                for element in elements[:10]:  # Limit to prevent too much text
                    if element_type == "links":
                        elements_info += f"    - {element.get('text', 'No text')} -> {element.get('href', 'No href')}\n"
                    elif element_type == "buttons":
                        elements_info += f"    - {element.get('text', 'No text')}\n"
                    elif element_type == "inputs":
                        elements_info += f"    - {element.get('type', 'text')} input: {element.get('name', 'No name')}\n"
                    else:
                        elements_info += f"    - {element}\n"
                
                if len(elements) > 10:
                    elements_info += f"    - ... and {len(elements) - 10} more\n"
        
        return {
            "pages": pages_info,
            "elements": elements_info
        }
    
    async def _parse_business_flows(self, llm_response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response to extract business flows.
        
        Args:
            llm_response: LLM response text
            
        Returns:
            List of business flow dictionaries
        """
        flows = []
        
        # Use a more structured approach with the LLM
        system_message = """
        Parse the previous analysis into a structured JSON format for each business flow.
        Each business flow should have the following fields:
        - name: String
        - description: String
        - priority: Integer (1-5)
        - starting_point: String
        - steps: Array of Strings
        - success_criteria: Array of Strings
        """
        
        prompt = f"""
        Convert your analysis into structured business flows in JSON format:
        
        {llm_response}
        """
        
        try:
            # Get structured completion from LLM
            structured_response = await self.llm.get_completion(prompt, system_message)
            
            # Parse JSON response
            from aiqatester.llm.response_parser import ResponseParser
            parsed_data = ResponseParser.extract_json(structured_response)
            
            if parsed_data:
                if isinstance(parsed_data, list):
                    flows = parsed_data
                elif isinstance(parsed_data, dict) and "flows" in parsed_data:
                    flows = parsed_data["flows"]
                elif isinstance(parsed_data, dict):
                    # Single flow
                    flows = [parsed_data]
            
        except Exception as e:
            logger.error(f"Error parsing business flows: {e}")
            
            # Fallback to simple parsing
            import re
            
            # Look for flow names (assuming they start with "Flow" or have a number prefix)
            flow_blocks = re.split(r'\n\s*\d+\.\s+|\n\s*Flow\s+\d+:', llm_response)
            
            for block in flow_blocks:
                if not block.strip():
                    continue
                
                flow = {}
                
                # Try to extract name
                name_match = re.search(r'(?:Name|Title):\s*([^\n]+)', block)
                if name_match:
                    flow["name"] = name_match.group(1).strip()
                else:
                    # Use first line as name
                    first_line = block.strip().split('\n')[0]
                    flow["name"] = first_line[:50]  # Limit to 50 chars
                
                # Try to extract description
                desc_match = re.search(r'Description:\s*([^\n]+(?:\n\s+[^\n]+)*)', block)
                if desc_match:
                    flow["description"] = desc_match.group(1).strip()
                else:
                    flow["description"] = "No description available"
                
                # Try to extract priority
                priority_match = re.search(r'Priority:\s*(\d+)', block)
                if priority_match:
                    flow["priority"] = int(priority_match.group(1))
                else:
                    flow["priority"] = 3  # Default priority
                
                # Try to extract steps
                steps_match = re.search(r'Steps:\s*((?:[^\n]*\n\s*)+)', block)
                if steps_match:
                    steps_text = steps_match.group(1)
                    steps = re.findall(r'(?:\d+\.\s*|\-\s*)([^\n]+)', steps_text)
                    flow["steps"] = [step.strip() for step in steps]
                else:
                    flow["steps"] = []
                
                # Try to extract success criteria
                criteria_match = re.search(r'Success [Cc]riteria:\s*((?:[^\n]*\n\s*)+)', block)
                if criteria_match:
                    criteria_text = criteria_match.group(1)
                    criteria = re.findall(r'(?:\d+\.\s*|\-\s*)([^\n]+)', criteria_text)
                    flow["success_criteria"] = [criterion.strip() for criterion in criteria]
                else:
                    flow["success_criteria"] = []
                
                flows.append(flow)
        
        return flows
    
    async def analyze_page_business_functions(self, url: str) -> Dict[str, Any]:
        """
        Analyze the business functions of a specific page.
        
        Args:
            url: URL of the page to analyze
            
        Returns:
            Dictionary of business functions
        """
        try:
            # Navigate to the page
            await self.browser.navigate(url)
            
            # Get page content
            page_text = await self.browser.get_page_text()
            
            # Extract interactive elements
            elements = await self.browser.extract_interactive_elements()
            
            # Prepare input for LLM
            elements_text = ""
            for element_type, element_list in elements.items():
                elements_text += f"{element_type.capitalize()}:\n"
                for i, element in enumerate(element_list[:10]):
                    if element_type == "links":
                        elements_text += f"  - {element.get('text', 'No text')} -> {element.get('href', 'No href')}\n"
                    elif element_type == "buttons":
                        elements_text += f"  - {element.get('text', 'No text')}\n"
                    elif element_type == "inputs":
                        elements_text += f"  - {element.get('type', 'text')} input: {element.get('name', 'No name')}\n"
                    else:
                        elements_text += f"  - {element}\n"
                
                if len(element_list) > 10:
                    elements_text += f"  - ... and {len(element_list) - 10} more\n"
            
            # Send to LLM for analysis
            system_message = """
            You are an expert QA tester with deep understanding of web applications.
            Analyze the provided page content and identify business functions and purposes.
            """
            
            prompt = f"""
            Analyze the following webpage and identify its business functions and purpose:
            
            URL: {url}
            
            Page Content (excerpt):
            {page_text[:2000]}... [truncated]
            
            Interactive Elements:
            {elements_text}
            
            Identify:
            1. What is the primary business purpose of this page?
            2. What functions can users perform on this page?
            3. How does this page fit into potential business flows?
            4. What would be important to test on this page?
            """
            
            response = await self.llm.get_completion(prompt, system_message)
            
            # Extract structured information
            system_message_structured = """
            Convert your analysis into a structured JSON format with the following fields:
            - page_purpose: String
            - business_functions: Array of Strings
            - business_flows: Array of Strings
            - testing_priorities: Array of Strings
            """
            
            structured_response = await self.llm.get_completion(response, system_message_structured)
            
            # Parse JSON response
            from aiqatester.llm.response_parser import ResponseParser
            parsed_data = ResponseParser.extract_json(structured_response)
            
            if not parsed_data:
                # Create a basic structure if parsing failed
                parsed_data = {
                    "page_purpose": "Unknown",
                    "business_functions": [],
                    "business_flows": [],
                    "testing_priorities": []
                }
            
            logger.info(f"Analyzed business functions for {url}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error analyzing page business functions for {url}: {e}")
            return {
                "page_purpose": "Error",
                "business_functions": [],
                "business_flows": [],
                "testing_priorities": []
            }