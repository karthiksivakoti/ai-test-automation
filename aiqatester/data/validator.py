# ai-test-automation/aiqatester/data/validator.py
"""
Data Validator module for AIQATester.

This module validates test data against requirements.
"""

from typing import Dict, List, Any, Tuple, Union
import re

from loguru import logger

class DataValidator:
    """Validates test data against requirements."""
    
    def __init__(self):
        """Initialize the data validator."""
        logger.info("DataValidator initialized")
        
    def validate_data(self, data: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate test data against requirements.
        
        Args:
            data: Test data to validate
            requirements: Data requirements
            
        Returns:
            Validation results
        """
        # Get specific requirements
        data_requirements = requirements.get("requirements", {})
        
        # Initialize validation results
        results = {
            "valid": True,
            "issues": []
        }
        
        # Validate each field
        for field, required_value in data_requirements.items():
            # Skip if no specific requirements
            if required_value is None:
                continue
            
            # Check if field exists in data
            if field not in data:
                results["valid"] = False
                results["issues"].append({
                    "field": field,
                    "error": "Field is missing",
                    "required": required_value,
                    "actual": None
                })
                continue
            
            # Get actual value
            actual_value = data[field]
            
            # Validate field
            valid, error = self._validate_field(field, actual_value, required_value)
            
            if not valid:
                results["valid"] = False
                results["issues"].append({
                    "field": field,
                    "error": error,
                    "required": required_value,
                    "actual": actual_value
                })
        
        logger.info(f"Validated data: {len(data)} fields, {len(results['issues'])} issues")
        return results
    
    def _validate_field(self, field: str, actual_value: Any, required_value: Any) -> Tuple[bool, str]:
        """
        Validate a specific field.
        
        Args:
            field: Field name
            actual_value: Actual value
            required_value: Required value
            
        Returns:
            Tuple of (valid, error_message)
        """
        field_lower = field.lower()
        
        # If required_value is a dict with specific constraints
        if isinstance(required_value, dict):
            return self._validate_with_constraints(field, actual_value, required_value)
        
        # If required_value is a specific value
        if required_value != actual_value:
            return False, f"Value does not match required value: {required_value}"
        
        # Validate based on field type
        if "email" in field_lower:
            return self._validate_email(actual_value)
        
        elif "password" in field_lower:
            return self._validate_password(actual_value)
        
        elif "phone" in field_lower:
            return self._validate_phone(actual_value)
        
        elif "credit_card" in field_lower or "card_number" in field_lower:
            return self._validate_credit_card(actual_value)
        
        elif "cvv" in field_lower:
            return self._validate_cvv(actual_value)
        
        elif "date" in field_lower:
            return self._validate_date(actual_value)
        
        # Default to valid
        return True, ""
    
    def _validate_with_constraints(self, field: str, actual_value: Any, constraints: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a field against constraints.
        
        Args:
            field: Field name
            actual_value: Actual value
            constraints: Validation constraints
            
        Returns:
            Tuple of (valid, error_message)
        """
        field_lower = field.lower()
        
        # Check min length
        if "min_length" in constraints and len(str(actual_value)) < constraints["min_length"]:
            return False, f"Value length {len(str(actual_value))} is less than minimum length {constraints['min_length']}"
        
        # Check max length
        if "max_length" in constraints and len(str(actual_value)) > constraints["max_length"]:
            return False, f"Value length {len(str(actual_value))} is greater than maximum length {constraints['max_length']}"
        
        # Check pattern
        if "pattern" in constraints and not re.match(constraints["pattern"], str(actual_value)):
            return False, f"Value does not match required pattern: {constraints['pattern']}"
        
        # Check min value
        if "min_value" in constraints:
            try:
                if float(actual_value) < float(constraints["min_value"]):
                    return False, f"Value {actual_value} is less than minimum value {constraints['min_value']}"
            except (ValueError, TypeError):
                return False, f"Value {actual_value} cannot be compared to minimum value {constraints['min_value']}"
        
        # Check max value
        if "max_value" in constraints:
            try:
                if float(actual_value) > float(constraints["max_value"]):
                    return False, f"Value {actual_value} is greater than maximum value {constraints['max_value']}"
            except (ValueError, TypeError):
                return False, f"Value {actual_value} cannot be compared to maximum value {constraints['max_value']}"
        
        # Check enum values
        if "enum" in constraints and actual_value not in constraints["enum"]:
            return False, f"Value {actual_value} is not in allowed values: {', '.join(map(str, constraints['enum']))}"
        
        # Check type
        if "type" in constraints:
            if constraints["type"] == "number":
                try:
                    float(actual_value)
                except (ValueError, TypeError):
                    return False, f"Value {actual_value} is not a number"
            elif constraints["type"] == "integer":
                try:
                    int(actual_value)
                except (ValueError, TypeError):
                    return False, f"Value {actual_value} is not an integer"
            elif constraints["type"] == "boolean":
                if not isinstance(actual_value, bool) and str(actual_value).lower() not in ("true", "false", "1", "0"):
                    return False, f"Value {actual_value} is not a boolean"
        
        # Specific field validations
        if "email" in field_lower:
            return self._validate_email(actual_value)
        
        elif "password" in field_lower:
            return self._validate_password(actual_value)
        
        elif "phone" in field_lower:
            return self._validate_phone(actual_value)
        
        elif "credit_card" in field_lower or "card_number" in field_lower:
            return self._validate_credit_card(actual_value)
        
        elif "cvv" in field_lower:
            return self._validate_cvv(actual_value)
        
        elif "date" in field_lower:
            return self._validate_date(actual_value)
        
        # Default to valid
        return True, ""
    
    def _validate_email(self, value: str) -> Tuple[bool, str]:
        """
        Validate an email address.
        
        Args:
            value: Email address to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, value):
            return False, f"Invalid email address: {value}"
        return True, ""
    
    def _validate_password(self, value: str) -> Tuple[bool, str]:
        """
        Validate a password.
        
        Args:
            value: Password to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        if len(value) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r"[A-Z]", value):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r"[a-z]", value):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r"[0-9]", value):
            return False, "Password must contain at least one digit"
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    def _validate_phone(self, value: str) -> Tuple[bool, str]:
        """
        Validate a phone number.
        
        Args:
            value: Phone number to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        # Strip non-digits
        digits = re.sub(r"\D", "", value)
        
        if len(digits) < 10:
            return False, f"Phone number must have at least 10 digits: {value}"
        
        return True, ""
    
    def _validate_credit_card(self, value: str) -> Tuple[bool, str]:
        """
        Validate a credit card number.
        
        Args:
            value: Credit card number to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        # Strip non-digits
        digits = re.sub(r"\D", "", value)
        
        if len(digits) < 13 or len(digits) > 19:
            return False, f"Credit card number must have 13-19 digits: {value}"
        
        # Check if starts with valid prefix
        valid_prefixes = ["4", "5", "3", "6"]  # Visa, Mastercard, Amex, Discover
        if not any(digits.startswith(prefix) for prefix in valid_prefixes):
            return False, f"Credit card number must start with a valid prefix (4, 5, 3, 6): {value}"
        
        return True, ""
    
    def _validate_cvv(self, value: str) -> Tuple[bool, str]:
        """
        Validate a CVV.
        
        Args:
            value: CVV to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        # Strip non-digits
        digits = re.sub(r"\D", "", value)
        
        if len(digits) not in (3, 4):
            return False, f"CVV must have 3 or 4 digits: {value}"
        
        return True, ""
    
    def _validate_date(self, value: str) -> Tuple[bool, str]:
        """
        Validate a date.
        
        Args:
            value: Date to validate
            
        Returns:
            Tuple of (valid, error_message)
        """
        # Check if it's in YYYY-MM-DD format
        if re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            try:
                year, month, day = map(int, value.split("-"))
                
                # Check if month is valid
                if month < 1 or month > 12:
                    return False, f"Invalid month in date: {value}"
                
                # Check if day is valid
                days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                
                # Adjust for leap year
                if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
                    days_in_month[2] = 29
                
                if day < 1 or day > days_in_month[month]:
                    return False, f"Invalid day in date: {value}"
                
                return True, ""
            except ValueError:
                return False, f"Invalid date format: {value}"
        
        # Check if it's in MM/YY format (credit card expiry)
        elif re.match(r"^\d{1,2}/\d{2}$", value):
            try:
                month, year = map(int, value.split("/"))
                
                # Check if month is valid
                if month < 1 or month > 12:
                    return False, f"Invalid month in date: {value}"
                
                return True, ""
            except ValueError:
                return False, f"Invalid date format: {value}"
        
        return False, f"Invalid date format: {value}"