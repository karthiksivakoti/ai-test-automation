# ai-test-automation/aiqatester/llm/response_parser.py
"""
Response Parser module for AIQATester.

This module parses and processes LLM responses.
"""

from typing import Dict, List, Any, Optional, Union
import json
import re

class ResponseParser:
    """Parses and processes LLM responses."""
    
    @staticmethod
    def extract_json(response: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from an LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            Extracted JSON as a dictionary, or None if extraction failed
        """
        # Try to find JSON in code blocks
        json_match = re.search(r"```(?:json)?(\n|\r\n)(.+?)(\n|\r\n)```", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(2)
        else:
            # Try to find JSON between curly braces
            json_match = re.search(r"\{(.+)\}", response, re.DOTALL)
            if json_match:
                json_str = "{" + json_match.group(1) + "}"
            else:
                # Use the whole response
                json_str = response
        
        try:
            return json.loads(json_str)
        except Exception:
            return None
    
    @staticmethod
    def extract_list(response: str) -> List[str]:
        """
        Extract a list from an LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            Extracted list of items
        """
        # Look for numbered list items (1. Item)
        numbered_items = re.findall(r"^\d+\.\s+(.+?)(?=\n\d+\.|\n\n|\Z)", response, re.MULTILINE | re.DOTALL)
        if numbered_items:
            return [item.strip() for item in numbered_items]
            
        # Look for bullet list items (- Item or * Item)
        bullet_items = re.findall(r"^[\-\*]\s+(.+?)(?=\n[\-\*]|\n\n|\Z)", response, re.MULTILINE | re.DOTALL)
        if bullet_items:
            return [item.strip() for item in bullet_items]
            
        # Split by newlines if no list format is detected
        return [line.strip() for line in response.split("\n") if line.strip()]
    
    @staticmethod
    def extract_test_cases(response: str) -> List[Dict[str, Any]]:
        """
        Extract test cases from an LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            List of test cases
        """
        # Try to extract JSON
        json_data = ResponseParser.extract_json(response)
        if json_data:
            # If it's already a list, return it
            if isinstance(json_data, list):
                return json_data
            
            # If it's a dictionary with a 'test_cases' key, return the value
            if isinstance(json_data, dict) and 'test_cases' in json_data:
                return json_data['test_cases']
            
            # Otherwise, return the dictionary as a single-item list
            return [json_data]
        
        # If JSON extraction failed, try to parse using regex
        test_cases = []
        
        # Look for test case blocks
        test_case_blocks = re.split(r"\n\s*#{1,3}\s+Test Case \d+:|\n\s*Test Case \d+:", response)
        
        for block in test_case_blocks:
            if not block.strip():
                continue
            
            test_case = {}
            
            # Extract name
            name_match = re.search(r"(?:Name|Title):\s*(.+?)(?:\n|$)", block)
            if name_match:
                test_case["name"] = name_match.group(1).strip()
            else:
                # Use first line as name
                first_line = block.strip().split("\n")[0]
                test_case["name"] = first_line
            
            # Extract description
            desc_match = re.search(r"Description:\s*(.+?)(?:\n\s*\w+:|\n\n|\Z)", block, re.DOTALL)
            if desc_match:
                test_case["description"] = desc_match.group(1).strip()
            
            # Extract priority
            priority_match = re.search(r"Priority:\s*(\d+|critical|high|medium|low)", block, re.IGNORECASE)
            if priority_match:
                priority_text = priority_match.group(1).lower()
                priority_map = {"critical": 5, "high": 4, "medium": 3, "low": 2}
                try:
                    test_case["priority"] = priority_map.get(priority_text, int(priority_text))
                except ValueError:
                    test_case["priority"] = 3  # Default priority
            
            # Extract preconditions
            precond_match = re.search(r"Preconditions:\s*(.+?)(?:\n\s*\w+:|\n\n|\Z)", block, re.DOTALL)
            if precond_match:
                precond_text = precond_match.group(1)
                preconditions = [item.strip() for item in re.findall(r"(?:^\d+\.\s*|\n\s*\d+\.\s*|\n\s*-\s*)(.+?)(?=\n\s*\d+\.|\n\s*-|\Z)", precond_text, re.DOTALL)]
                if not preconditions:
                    preconditions = [item.strip() for item in precond_text.split("\n") if item.strip()]
                test_case["preconditions"] = preconditions
            
            # Extract steps
            steps_match = re.search(r"Steps?:\s*(.+?)(?:\n\s*\w+:|\n\n|\Z)", block, re.DOTALL)
            if steps_match:
                steps_text = steps_match.group(1)
                step_items = re.findall(r"(?:^\d+\.\s*|\n\s*\d+\.\s*)(.+?)(?=\n\s*\d+\.|\Z)", steps_text, re.DOTALL)
                steps = []
                for i, step_text in enumerate(step_items):
                    steps.append({
                        "step": i + 1,
                        "action": step_text.strip()
                    })
                test_case["steps"] = steps
            
            # Extract expected results
            expected_match = re.search(r"Expected Results?:\s*(.+?)(?:\n\s*\w+:|\n\n|\Z)", block, re.DOTALL)
            if expected_match:
                expected_text = expected_match.group(1)
                expected_results = [item.strip() for item in re.findall(r"(?:^\d+\.\s*|\n\s*\d+\.\s*|\n\s*-\s*)(.+?)(?=\n\s*\d+\.|\n\s*-|\Z)", expected_text, re.DOTALL)]
                if not expected_results:
                    expected_results = [item.strip() for item in expected_text.split("\n") if item.strip()]
                test_case["expected_results"] = expected_results
            
            # Only add the test case if it has at least a name and steps
            if "name" in test_case and ("steps" in test_case or "description" in test_case):
                test_cases.append(test_case)
        
        return test_cases