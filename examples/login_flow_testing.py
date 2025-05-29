#  ai-test-automation/examples/login_flow_testing.py
"""
Example: Login Flow Testing

This example demonstrates testing of a login flow.
"""

import asyncio
import os
from dotenv import load_dotenv

from aiqatester.director import TestDirector
from aiqatester.utils.config import Config
from aiqatester.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logger
logger = setup_logger()

async def main():
    """Run the login testing example."""
    # Create configuration
    config = Config()
    
    # Create test director
    director = TestDirector(config)
    
    # Define the website URL and task
    url = "https://example-login-site.com"
    task = """
    Test the login flow with various scenarios:
    1. Successful login with valid credentials
    2. Failed login with invalid credentials
    3. Validation of error messages
    4. Password reset functionality
    5. Remember me feature
    """
    
    # Run tests
    results = await director.run(url, task)
    
    # Print results
    print("Testing completed!")
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())
