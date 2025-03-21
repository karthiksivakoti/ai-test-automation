# ai-test-automation/aiqatester/generator/data_requirements.py
"""
Data Requirements module for AIQATester.

This module identifies data requirements for test cases.
"""

from typing import Dict, List, Any

from loguru import logger

class DataRequirements:
    """Identifies data requirements for test cases."""
    
    def __init__(self):
        """Initialize the data requirements analyzer."""
        logger.info("DataRequirements initialized")
        
    def identify_requirements(self, test_script: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify data requirements for a test script.
        
        Args:
            test_script: The test script
            
        Returns:
            Dictionary of data requirements
        """
        logger.info(f"Identifying data requirements for test script: {test_script.get('name', 'Unknown')}")
        
        requirements = {}
        
        # Check for explicit data requirements in the script
        if "data_requirements" in test_script:
            requirements.update(test_script["data_requirements"])
        
        # Analyze steps for implicit data requirements
        for step in test_script.get("steps", []):
            # Skip if not a dict
            if not isinstance(step, dict):
                continue
                
            action = step.get("action", "").lower()
            selector = step.get("selector", "")
            value = step.get("value", "")
            
            # Check for data needs based on step action and selector
            if ("type" in action or "fill" in action or "input" in action) and value:
                # Identify data type from selector and action
                data_type = self._identify_data_type(selector, action)
                
                # Skip if already added
                if data_type in requirements:
                    continue
                
                # Add requirement with default value
                requirements[data_type] = value
        
        # Add default values for common data types if not present
        self._add_default_requirements(requirements)
        
        # Validate data types and requirements
        validated_requirements = self._validate_requirements(requirements)
        
        return {
            "requirements": validated_requirements,
            "placeholder_pattern": r"\{([^}]+)\}"  # Regex pattern for placeholders like {username}
        }
    
    def _identify_data_type(self, selector: str, action: str) -> str:
        """
        Identify data type from selector and action.
        
        Args:
            selector: Element selector
            action: Step action
            
        Returns:
            Data type identifier
        """
        selector_lower = selector.lower()
        action_lower = action.lower()
        
        # Check for common input types
        if "email" in selector_lower or "email" in action_lower:
            return "email"
        elif "password" in selector_lower or "password" in action_lower:
            return "password"
        elif "username" in selector_lower or "username" in action_lower or "user" in selector_lower:
            return "username"
        elif "name" in selector_lower:
            if "first" in selector_lower:
                return "first_name"
            elif "last" in selector_lower:
                return "last_name"
            else:
                return "name"
        elif "phone" in selector_lower:
            return "phone"
        elif "address" in selector_lower:
            if "street" in selector_lower:
                return "street_address"
            elif "city" in selector_lower:
                return "city"
            elif "state" in selector_lower:
                return "state"
            elif "zip" in selector_lower or "postal" in selector_lower:
                return "zip_code"
            else:
                return "address"
        elif "search" in selector_lower or "search" in action_lower:
            return "search_query"
        elif "credit" in selector_lower or "card" in selector_lower:
            if "number" in selector_lower:
                return "credit_card_number"
            elif "cvv" in selector_lower or "cvc" in selector_lower:
                return "cvv"
            elif "expiry" in selector_lower or "expiration" in selector_lower:
                return "card_expiry"
            else:
                return "credit_card"
        
        # Default to input_text if no specific type identified
        return "input_text"
    
    def _add_default_requirements(self, requirements: Dict[str, Any]) -> None:
        """
        Add default values for common data types if not present.
        
        Args:
            requirements: Data requirements dictionary (modified in-place)
        """
        # Default values for common data types
        defaults = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "username": "testuser",
            "name": "Test User",
            "first_name": "Test",
            "last_name": "User",
            "phone": "123-456-7890",
            "address": "123 Test Street",
            "street_address": "123 Test Street",
            "city": "Test City",
            "state": "Test State",
            "zip_code": "12345",
            "search_query": "test search",
            "credit_card_number": "4111111111111111",
            "cvv": "123",
            "card_expiry": "12/25"
        }
        
        # Add defaults for missing types
        for data_type, default_value in defaults.items():
            if data_type not in requirements:
                # Only add if any related type is present
                # (e.g., add phone only if address is present)
                related_types = {
                    "street_address": ["address", "city", "state", "zip_code"],
                    "city": ["address", "street_address", "state", "zip_code"],
                    "state": ["address", "street_address", "city", "zip_code"],
                    "zip_code": ["address", "street_address", "city", "state"],
                    "credit_card_number": ["cvv", "card_expiry"],
                    "cvv": ["credit_card_number", "card_expiry"],
                    "card_expiry": ["credit_card_number", "cvv"],
                    "first_name": ["name", "last_name"],
                    "last_name": ["name", "first_name"]
                }
                
                # Check if any related type exists
                if data_type in related_types:
                    for related_type in related_types[data_type]:
                        if related_type in requirements:
                            requirements[data_type] = default_value
                            break
    
    def _validate_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate data requirements.
        
        Args:
            requirements: Data requirements dictionary
            
        Returns:
            Validated requirements
        """
        validated = {}
        
        # Validators for common data types
        validators = {
            "email": lambda v: "@" in v and "." in v.split("@")[1],
            "password": lambda v: len(v) >= 8,
            "phone": lambda v: len(v.replace("-", "").replace(" ", "")) >= 10,
            "zip_code": lambda v: len(v.replace("-", "")) >= 5,
            "credit_card_number": lambda v: len(v.replace(" ", "").replace("-", "")) >= 13,
            "cvv": lambda v: len(v) >= 3 and v.isdigit(),
            "card_expiry": lambda v: "/" in v and len(v.split("/")[0]) <= 2 and len(v.split("/")[1]) <= 4
        }
        
        # Validate each requirement
        for data_type, value in requirements.items():
            # Skip if value is None
            if value is None:
                validated[data_type] = None
                continue
                
            # Validate if validator exists
            if data_type in validators and not validators[data_type](value):
                # Generate a valid value
                if data_type == "email":
                    validated[data_type] = "test@example.com"
                elif data_type == "password":
                    validated[data_type] = "TestPassword123!"
                elif data_type == "phone":
                    validated[data_type] = "123-456-7890"
                elif data_type == "zip_code":
                    validated[data_type] = "12345"
                elif data_type == "credit_card_number":
                    validated[data_type] = "4111111111111111"
                elif data_type == "cvv":
                    validated[data_type] = "123"
                elif data_type == "card_expiry":
                    validated[data_type] = "12/25"
                else:
                    validated[data_type] = value
            else:
                validated[data_type] = value
        
        return validated