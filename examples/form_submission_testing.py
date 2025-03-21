# ai-test-automation/examples/form_submission_testing.py
"""
Example: Form Submission Testing

This example demonstrates testing of form submission.
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
    """Run the form testing example."""
    # Create configuration
    config = Config()
    
    # Create test director
    director = TestDirector(config)
    
    # Define the website URL and task
    url = "https://example-form-site.com"
    task = """
    Test the contact form submission with various inputs:
    1. Submit with all valid fields
    2. Test validation of required fields
    3. Test validation of email format
    4. Test character limits
    5. Test handling of special characters
    6. Verify success and error messages
    """
    
    # Run tests
    results = await director.run(url, task)
    
    # Print results
    print("Testing completed!")
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())