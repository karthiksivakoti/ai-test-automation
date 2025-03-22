# ai-test-automation/aiqatester/director.py
"""
Test Director module for AIQATester.

This module orchestrates the entire testing process, including website analysis,
test planning, test generation, execution, and feedback processing.
"""

import asyncio
from typing import Dict, List, Optional, Any

from loguru import logger

from aiqatester.analyzer.site_analyzer import SiteAnalyzer
from aiqatester.analyzer.business_analyzer import BusinessAnalyzer
from aiqatester.knowledge.site_model import SiteModel
from aiqatester.planner.strategy import TestStrategy
from aiqatester.generator.script_generator import TestScriptGenerator
from aiqatester.executor.runner import TestRunner
from aiqatester.feedback.analyzer import FeedbackAnalyzer
from aiqatester.utils.config import Config
from aiqatester.browser.controller import BrowserController
from aiqatester.llm.openai_client import OpenAIClient
from aiqatester.utils.data_exporter import DataExporter

class TestDirector:
    """Orchestrates the entire testing process."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the test director.
        
        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self.browser = None
        self.llm_client = None
        self.data_exporter = DataExporter()
        logger.info("TestDirector initialized")
        
    async def initialize(self) -> None:
        """Initialize components."""
        # Initialize browser controller
        self.browser = BrowserController(
            headless=self.config.headless,
            browser_type=self.config.browser_type,
            slow_mo=self.config.slow_mo,
            viewport_size={
                "width": self.config.viewport_width,
                "height": self.config.viewport_height
            },
            timeout=self.config.timeout,
            screenshot_dir=self.config.screenshot_dir
        )
        
        # Initialize LLM client
        if self.config.llm_provider == "openai":
            self.llm_client = OpenAIClient(model=self.config.openai_model)
        elif self.config.llm_provider == "anthropic":
            from aiqatester.llm.anthropic_client import AnthropicClient
            self.llm_client = AnthropicClient(model=self.config.anthropic_model)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm_provider}")
        
        # Start browser
        await self.browser.start()
        
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.browser:
            await self.browser.stop()
        
    async def run(self, url: str, task: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the complete testing process.
        
        Args:
            url: The website URL to test
            task: Optional task description
            
        Returns:
            Testing results
        """
        try:
            # Initialize components if not already initialized
            if not self.browser or not self.llm_client:
                await self.initialize()
            
            logger.info(f"Starting test process for URL: {url}")
            if task:
                logger.info(f"Task description: {task}")
            
            # Step 1: Analyze the website
            site_model = await self._analyze_website(url)
            self.data_exporter.export_site_model(site_model)
            
            # Step 2: Create a testing strategy
            test_strategy = await self._create_test_strategy(site_model, task)
            self.data_exporter.export_test_strategy(test_strategy)
            
            # Step 3: Generate test scripts
            test_scripts = await self._generate_test_scripts(site_model, test_strategy)
            self.data_exporter.export_test_scripts(test_scripts)

            # Step 4: Execute tests
            test_results = await self._execute_tests(test_scripts)
            self.data_exporter.export_test_results(test_results)
            
            # Step 5: Process feedback
            feedback = await self._process_feedback(test_results)
            
            # Step 6: Enhance tests (for future runs)
            enhanced_tests = await self._enhance_tests(test_scripts, feedback)
            
            # Return results
            return {
                "url": url,
                "task": task,
                "site_analysis": {
                    "page_count": site_model.get_page_count(),
                    "interactive_elements": site_model.get_interactive_element_count()
                },
                "test_execution": {
                    "total_tests": len(test_scripts),
                    "passed": test_results.get("passed", 0),
                    "failed": test_results.get("failed", 0)
                },
                "test_results": test_results,
                "feedback": feedback
            }
            
        except Exception as e:
            logger.error(f"Error running test process: {e}")
            raise
        finally:
            # Clean up resources
            await self.cleanup()
    
    async def _analyze_website(self, url: str) -> SiteModel:
        """
        Analyze the website.
        
        Args:
            url: The website URL to analyze
            
        Returns:
            SiteModel containing website information
        """
        logger.info(f"Analyzing website: {url}")
        
        # Create site analyzer
        site_analyzer = SiteAnalyzer(self.browser)
        
        # Analyze site structure
        site_model = await site_analyzer.analyze_site(
            url, 
            max_depth=self.config.max_depth
        )
        
        # Analyze business logic
        business_analyzer = BusinessAnalyzer(self.browser, self.llm_client)
        business_flows = await business_analyzer.identify_business_flows(site_model)
        
        # Add business flows to site model
        for flow in business_flows.get("flows", []):
            site_model.add_business_flow(flow)
        
        logger.info(f"Website analysis completed: {site_model.get_page_count()} pages analyzed")
        return site_model
    
    async def _create_test_strategy(self, site_model: SiteModel, task: Optional[str]) -> Dict[str, Any]:
        """
        Create a testing strategy.
        
        Args:
            site_model: Site model containing website information
            task: Optional task description
            
        Returns:
            Dictionary containing the testing strategy
        """
        logger.info("Creating test strategy")
        
        # Create test strategy planner
        strategy_planner = TestStrategy(site_model, self.llm_client)
        
        # Create strategy
        if task:
            # If task is provided, use it to guide the strategy
            strategy = await strategy_planner.create_strategy_for_task(task)
        else:
            # Otherwise, create a general strategy
            strategy = await strategy_planner.create_strategy()
        
        # Apply priority limits
        if self.config.max_test_cases > 0:
            # Limit the number of test cases
            from aiqatester.planner.prioritizer import TestPrioritizer
            prioritizer = TestPrioritizer()
            prioritized_tests = prioritizer.prioritize_tests(strategy.get("test_cases", []))
            strategy["test_cases"] = prioritized_tests[:self.config.max_test_cases]
        
        logger.info(f"Test strategy created with {len(strategy.get('test_cases', []))} test cases")
        return strategy
    
    async def _generate_test_scripts(self, site_model: SiteModel, test_strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate test scripts.
        
        Args:
            site_model: Site model containing website information
            test_strategy: Testing strategy
            
        Returns:
            List of test scripts
        """
        logger.info("Generating test scripts")
        
        # Create test script generator
        script_generator = TestScriptGenerator(site_model, self.llm_client)
        
        # Generate scripts
        test_scripts = await script_generator.generate_scripts(test_strategy)
        
        logger.info(f"Generated {len(test_scripts)} test scripts")
        return test_scripts
    
    async def _execute_tests(self, test_scripts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute test scripts.
        
        Args:
            test_scripts: List of test scripts to execute
            
        Returns:
            Test results
        """
        logger.info(f"Executing {len(test_scripts)} test scripts")
        
        # Create test runner
        test_runner = TestRunner(self.browser)
        
        # Execute tests
        test_results = await test_runner.run_test_suite(test_scripts)
        
        # Generate report
        from aiqatester.executor.reporter import TestReporter
        reporter = TestReporter()
        report = reporter.generate_report(test_results)
        
        # Add report to results
        test_results["report"] = report
        
        logger.info(f"Test execution completed: {test_results.get('passed', 0)} passed, {test_results.get('failed', 0)} failed")
        return test_results
    
    async def _process_feedback(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process test results and generate feedback.
        
        Args:
            test_results: Test results
            
        Returns:
            Processed feedback
        """
        logger.info("Processing test results")
        
        # Create feedback analyzer
        feedback_analyzer = FeedbackAnalyzer(self.llm_client)
        
        # Analyze results
        feedback = await feedback_analyzer.analyze_results(test_results)
        
        logger.info("Feedback processing completed")
        return feedback
    
    async def _enhance_tests(self, test_scripts: List[Dict[str, Any]], feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Enhance test scripts based on feedback.
        
        Args:
            test_scripts: Original test scripts
            feedback: Feedback from test execution
            
        Returns:
            Enhanced test scripts
        """
        logger.info("Enhancing test scripts based on feedback")
        
        # Create test enhancer
        from aiqatester.feedback.enhancer import TestEnhancer
        enhancer = TestEnhancer(self.llm_client)
        
        # Enhance each test script
        enhanced_scripts = []
        for script in test_scripts:
            enhanced_script = await enhancer.enhance_test_script(script, feedback)
            enhanced_scripts.append(enhanced_script)
        
        logger.info(f"Test enhancement completed: {len(enhanced_scripts)} scripts enhanced")
        return enhanced_scripts