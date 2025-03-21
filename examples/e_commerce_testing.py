# ai-test-automation/examples/e_commerce_testing.py
"""
Example: E-commerce Website Testing

This example demonstrates testing of an e-commerce website.
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
    """Run the e-commerce testing example."""
    # Create configuration
    config = Config()
    
    # Create test director
    director = TestDirector(config)
    
    # Define the website URL and task
    url = "https://example-ecommerce-site.com"
    task = """
    Test the product search, filtering, and checkout process. Focus on these key workflows:
    1. Search for a product and verify search results
    2. Apply filters (price, category) and verify filtering works
    3. Add a product to cart
    4. Proceed to checkout and complete the purchase flow
    """
    
    # Run tests
    results = await director.run(url, task)
    
    # Print results
    print("Testing completed!")
    print(f"Results: {results}")

if __name__ == "__main__":
    asyncio.run(main())