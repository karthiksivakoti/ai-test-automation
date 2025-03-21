# ai-test-automation/aiqatester/data/generator.py
"""
Data Generator module for AIQATester.

This module generates test data based on requirements.
"""

from typing import Dict, List, Any, Optional
import random
import string
import datetime
import re

from loguru import logger

class DataGenerator:
    """Generates test data based on requirements."""
    
    def __init__(self):
        """Initialize the data generator."""
        logger.info("DataGenerator initialized")
    
    def generate_data(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate test data based on requirements.
        
        Args:
            requirements: Data requirements
            
        Returns:
            Generated test data
        """
        # Get the specific requirements or use empty dictionary
        data_requirements = requirements.get("requirements", {})
        
        # Generate data for each requirement
        generated_data = {}
        
        for field, value in data_requirements.items():
            # If value is already provided, use it
            if value is not None:
                generated_data[field] = value
                continue
            
            # Generate value based on field type
            generated_value = self._generate_value_for_field(field)
            generated_data[field] = generated_value
        
        logger.info(f"Generated test data for {len(generated_data)} fields")
        return generated_data
    
    def generate_default_data(self) -> Dict[str, Any]:
        """
        Generate default test data for common fields.
        
        Returns:
            Default test data
        """
        default_data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "name": "Test User",
            "phone": "123-456-7890",
            "address": "123 Test Street",
            "city": "Test City",
            "state": "Test State",
            "zip_code": "12345",
            "country": "United States",
            "credit_card": "4111111111111111",
            "credit_card_number": "4111111111111111",
            "cvv": "123",
            "card_expiry": "12/25",
            "search_query": "test search"
        }
        
        logger.info("Generated default test data")
        return default_data
    
    def _generate_value_for_field(self, field: str) -> Any:
        """
        Generate a value for a specific field.
        
        Args:
            field: Field name
            
        Returns:
            Generated value
        """
        field_lower = field.lower()
        
        # Email
        if "email" in field_lower:
            return self._generate_email()
        
        # Password
        elif "password" in field_lower:
            return self._generate_password()
        
        # Username
        elif "username" in field_lower or "user" in field_lower:
            return self._generate_username()
        
        # Name
        elif "name" in field_lower:
            if "first" in field_lower:
                return self._generate_first_name()
            elif "last" in field_lower:
                return self._generate_last_name()
            else:
                return self._generate_full_name()
        
        # Phone
        elif "phone" in field_lower:
            return self._generate_phone()
        
        # Address
        elif "address" in field_lower:
            if "street" in field_lower:
                return self._generate_street_address()
            elif "city" in field_lower:
                return self._generate_city()
            elif "state" in field_lower:
                return self._generate_state()
            elif "zip" in field_lower or "postal" in field_lower:
                return self._generate_zip()
            else:
                return self._generate_street_address()
        
        # Credit Card
        elif "credit" in field_lower or "card" in field_lower:
            if "number" in field_lower:
                return self._generate_credit_card_number()
            elif "cvv" in field_lower or "cvc" in field_lower:
                return self._generate_cvv()
            elif "expiry" in field_lower or "expiration" in field_lower:
                return self._generate_card_expiry()
            else:
                return self._generate_credit_card_number()
        
        # Date
        elif "date" in field_lower:
            if "birth" in field_lower:
                return self._generate_birth_date()
            else:
                return self._generate_date()
        
        # Search
        elif "search" in field_lower or "query" in field_lower:
            return self._generate_search_query()
        
        # Default to random string
        else:
            return self._generate_random_string(10)
    
    def _generate_email(self) -> str:
        """Generate a random email address."""
        domains = ["example.com", "test.com", "sample.org", "demo.net"]
        username = self._generate_random_string(8).lower()
        domain = random.choice(domains)
        return f"{username}@{domain}"
    
    def _generate_password(self) -> str:
        """Generate a random password."""
        # At least one uppercase, one lowercase, one digit, one special character
        uppercase = random.choice(string.ascii_uppercase)
        lowercase = ''.join(random.choices(string.ascii_lowercase, k=6))
        digit = random.choice(string.digits)
        special = random.choice("!@#$%^&*")
        
        # Combine and shuffle
        password = uppercase + lowercase + digit + special
        password_list = list(password)
        random.shuffle(password_list)
        return ''.join(password_list)
    
    def _generate_username(self) -> str:
        """Generate a random username."""
        prefixes = ["user", "test", "demo", "sample"]
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.digits, k=3))
        return f"{prefix}{suffix}"
    
    def _generate_first_name(self) -> str:
        """Generate a random first name."""
        first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry"]
        return random.choice(first_names)
    
    def _generate_last_name(self) -> str:
        """Generate a random last name."""
        last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
        return random.choice(last_names)
    
    def _generate_full_name(self) -> str:
        """Generate a random full name."""
        first_name = self._generate_first_name()
        last_name = self._generate_last_name()
        return f"{first_name} {last_name}"
    
    def _generate_phone(self) -> str:
        """Generate a random phone number."""
        area_code = ''.join(random.choices(string.digits, k=3))
        prefix = ''.join(random.choices(string.digits, k=3))
        line_number = ''.join(random.choices(string.digits, k=4))
        return f"{area_code}-{prefix}-{line_number}"
    
    def _generate_street_address(self) -> str:
        """Generate a random street address."""
        number = random.randint(1, 9999)
        streets = ["Main St", "Park Ave", "Oak Dr", "Maple Ln", "Washington Blvd", "Cedar Rd"]
        street = random.choice(streets)
        return f"{number} {street}"
    
    def _generate_city(self) -> str:
        """Generate a random city name."""
        cities = ["Springfield", "Riverdale", "Fairview", "Kingston", "Burlington", "Clinton", "Georgetown", "Salem"]
        return random.choice(cities)
    
    def _generate_state(self) -> str:
        """Generate a random state name."""
        states = ["California", "Texas", "Florida", "New York", "Illinois", "Pennsylvania", "Ohio", "Georgia"]
        return random.choice(states)
    
    def _generate_zip(self) -> str:
        """Generate a random ZIP code."""
        return ''.join(random.choices(string.digits, k=5))
    
    def _generate_credit_card_number(self) -> str:
        """Generate a random credit card number."""
        # Generate a valid Visa test number (starts with 4)
        return "4" + ''.join(random.choices(string.digits, k=15))
    
    def _generate_cvv(self) -> str:
        """Generate a random CVV."""
        return ''.join(random.choices(string.digits, k=3))
    
    def _generate_card_expiry(self) -> str:
        """Generate a random credit card expiry date."""
        # Generate a date in the future (1-5 years)
        current_year = datetime.datetime.now().year
        year = current_year + random.randint(1, 5)
        month = random.randint(1, 12)
        return f"{month:02d}/{year % 100:02d}"
    
    def _generate_date(self) -> str:
        """Generate a random date."""
        current_date = datetime.datetime.now()
        days = random.randint(1, 365)
        random_date = current_date + datetime.timedelta(days=days)
        return random_date.strftime("%Y-%m-%d")
    
    def _generate_birth_date(self) -> str:
        """Generate a random birth date."""
        # Generate a date in the past (18-65 years)
        current_year = datetime.datetime.now().year
        year = current_year - random.randint(18, 65)
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Using 28 to avoid invalid dates
        return f"{year}-{month:02d}-{day:02d}"
    
    def _generate_search_query(self) -> str:
        """Generate a random search query."""
        queries = [
            "test product",
            "example search",
            "how to use",
            "documentation",
            "tutorial",
            "getting started",
            "features and benefits"
        ]
        return random.choice(queries)
    
    def _generate_random_string(self, length: int) -> str:
        """Generate a random string of specified length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))