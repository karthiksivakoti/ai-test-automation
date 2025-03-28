# ai-test-automation/main.py
"""
Main entry point for AIQATester.

This module provides the main functionality and CLI interface.
"""

import asyncio
import argparse
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
    """Run AIQATester."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AIQATester - AI-Powered Automated Testing Framework")
    parser.add_argument("url", help="Website URL to test")
    parser.add_argument("--task", help="Testing task description")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--browser", choices=["chromium", "firefox", "webkit"], default="chromium", help="Browser type to use")
    parser.add_argument("--config", help="Path to configuration file")
    args = parser.parse_args()
    
    # Create configuration
    if args.config:
        config = Config.from_file(args.config)
    else:
        config = Config()
        
    # Override configuration with command line arguments
    if args.headless:
        config.headless = True
        
    if args.browser:
        config.browser_type = args.browser
    
    # Create test director
    director = TestDirector(config)
    
    # Run tests
    try:
        results = await director.run(args.url, args.task)
        print("Testing completed!")
        print(f"Results: {results}")
        print("\nDetailed information is available in these locations:")
        exports_dir = os.path.join(os.getcwd(), "exports")
        reports_dir = os.path.join(os.getcwd(), "reports")
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        
        # Find the latest export directory
        if os.path.exists(exports_dir):
            export_dirs = [d for d in os.listdir(exports_dir) if d.startswith("run_")]
            if export_dirs:
                latest_dir = max(export_dirs)
                print(f"- Site analysis: {os.path.join(exports_dir, latest_dir, 'site_model.json')}")
                print(f"- Test strategy: {os.path.join(exports_dir, latest_dir, 'test_strategy.json')}")
                print(f"- Test scripts: {os.path.join(exports_dir, latest_dir, 'test_scripts.json')}")
                print(f"- Test results: {os.path.join(exports_dir, latest_dir, 'test_results.json')}")
        
        print(f"- Test reports: {reports_dir}")
        print(f"- Screenshots: {screenshots_dir}")
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        raise
        
if __name__ == "__main__":
    asyncio.run(main())