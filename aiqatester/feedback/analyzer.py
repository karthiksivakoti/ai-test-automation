# ai-test-automation/aiqatester/feedback/analyzer.py
"""
Feedback Analyzer module for AIQATester.

This module analyzes test results and user feedback.
"""

from typing import Dict, List, Any

from loguru import logger

from aiqatester.llm.openai_client import OpenAIClient
from aiqatester.llm.response_parser import ResponseParser

class FeedbackAnalyzer:
    """Analyzes test results and user feedback."""
    
    def __init__(self, llm_client: OpenAIClient):
        """
        Initialize the feedback analyzer.
        
        Args:
            llm_client: LLM client for feedback analysis
        """
        self.llm = llm_client
        logger.info("FeedbackAnalyzer initialized")
        
    async def analyze_results(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test results.
        
        Args:
            test_results: Test results to analyze
            
        Returns:
            Analysis results
        """
        logger.info(f"Analyzing {len(test_results.get('results', []))} test results")
        
        # Extract key metrics
        metrics = self._extract_metrics(test_results)
        
        # Identify failure patterns
        failure_patterns = await self._identify_failure_patterns(test_results)
        
        # Generate insights
        insights = await self._generate_insights(test_results, metrics, failure_patterns)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(test_results, failure_patterns, insights)
        
        return {
            "metrics": metrics,
            "failure_patterns": failure_patterns,
            "insights": insights,
            "recommendations": recommendations
        }
        
    async def process_user_feedback(self, feedback: str, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user feedback.
        
        Args:
            feedback: User feedback text
            test_results: Related test results
            
        Returns:
            Processed feedback
        """
        logger.info("Processing user feedback")
        
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA analyst. Analyze the user feedback about test results
        and extract key insights and action items.
        """
        
        # Create a summary of test results
        summary = f"""
        Test Results Summary:
        - Total Tests: {test_results.get('total', 0)}
        - Passed: {test_results.get('passed', 0)}
        - Failed: {test_results.get('failed', 0)}
        - Skipped: {test_results.get('skipped', 0)}
        - Error: {test_results.get('error', 0)}
        """
        
        prompt = f"""
        Analyze the following user feedback about test results:
        
        User Feedback:
        {feedback}
        
        {summary}
        
        Extract key insights and specific action items from the feedback.
        """
        
        try:
            # Get completion from LLM
            response = await self.llm.get_completion(prompt, system_message)
            
            # Ask for structured output
            structured_prompt = """
            Convert your analysis into a structured JSON format with the following fields:
            - feedback_summary: Brief summary of user feedback
            - key_insights: Array of key insights extracted from the feedback
            - action_items: Array of specific action items based on the feedback
            - priority: Priority level for addressing the feedback (1-5, with 5 being highest)
            """
            
            structured_response = await self.llm.get_completion(structured_prompt)
            
            # Parse JSON response
            processed_feedback = ResponseParser.extract_json(structured_response)
            
            if not processed_feedback:
                # Create basic structure if parsing failed
                processed_feedback = {
                    "feedback_summary": "Failed to parse feedback",
                    "key_insights": [],
                    "action_items": [],
                    "priority": 3
                }
            
            logger.info(f"Processed user feedback with {len(processed_feedback.get('action_items', []))} action items")
            
            return processed_feedback
            
        except Exception as e:
            logger.error(f"Error processing user feedback: {e}")
            return {
                "feedback_summary": "Error processing feedback",
                "error": str(e),
                "key_insights": [],
                "action_items": [],
                "priority": 3
            }
    
    def _extract_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key metrics from test results.
        
        Args:
            test_results: Test results
            
        Returns:
            Key metrics
        """
        # Basic metrics
        metrics = {
            "total": test_results.get("total", 0),
            "passed": test_results.get("passed", 0),
            "failed": test_results.get("failed", 0),
            "skipped": test_results.get("skipped", 0),
            "error": test_results.get("error", 0),
            "duration": test_results.get("duration", 0)
        }
        
        # Calculate pass rate
        if metrics["total"] > 0:
            metrics["pass_rate"] = (metrics["passed"] / metrics["total"]) * 100
        else:
            metrics["pass_rate"] = 0
        
        # Calculate additional metrics
        step_metrics = self._calculate_step_metrics(test_results)
        assertion_metrics = self._calculate_assertion_metrics(test_results)
        
        # Add to metrics
        metrics.update(step_metrics)
        metrics.update(assertion_metrics)
        
        return metrics
    
    def _calculate_step_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate step metrics.
        
        Args:
            test_results: Test results
            
        Returns:
            Step metrics
        """
        step_metrics = {
            "total_steps": 0,
            "passed_steps": 0,
            "failed_steps": 0,
            "average_step_duration": 0
        }
        
        step_durations = []
        
        # Calculate step metrics
        for test_result in test_results.get("results", []):
            for step in test_result.get("steps", []):
                step_metrics["total_steps"] += 1
                
                if step.get("status") == "passed":
                    step_metrics["passed_steps"] += 1
                elif step.get("status") == "failed":
                    step_metrics["failed_steps"] += 1
                
                if "duration" in step:
                    step_durations.append(step["duration"])
        
        # Calculate average step duration
        if step_durations:
            step_metrics["average_step_duration"] = sum(step_durations) / len(step_durations)
        
        # Calculate step pass rate
        if step_metrics["total_steps"] > 0:
            step_metrics["step_pass_rate"] = (step_metrics["passed_steps"] / step_metrics["total_steps"]) * 100
        else:
            step_metrics["step_pass_rate"] = 0
        
        return step_metrics
    
    def _calculate_assertion_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate assertion metrics.
        
        Args:
            test_results: Test results
            
        Returns:
            Assertion metrics
        """
        assertion_metrics = {
            "total_assertions": 0,
            "passed_assertions": 0,
            "failed_assertions": 0
        }
        
        # Calculate assertion metrics
        for test_result in test_results.get("results", []):
            for assertion in test_result.get("assertions", []):
                assertion_metrics["total_assertions"] += 1
                
                if assertion.get("status") == "passed":
                    assertion_metrics["passed_assertions"] += 1
                elif assertion.get("status") == "failed":
                    assertion_metrics["failed_assertions"] += 1
        
        # Calculate assertion pass rate
        if assertion_metrics["total_assertions"] > 0:
            assertion_metrics["assertion_pass_rate"] = (assertion_metrics["passed_assertions"] / assertion_metrics["total_assertions"]) * 100
        else:
            assertion_metrics["assertion_pass_rate"] = 0
        
        return assertion_metrics
    
    async def _identify_failure_patterns(self, test_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify failure patterns in test results.
        
        Args:
            test_results: Test results
            
        Returns:
            List of failure patterns
        """
        patterns = []
        
        # Create a list of failed tests
        failed_tests = [test for test in test_results.get("results", []) if test.get("status") == "failed"]
        
        if not failed_tests:
            return patterns
        
        # Group failures by error message
        error_groups = {}
        for test in failed_tests:
            # Find the first failed step
            failed_step = next((step for step in test.get("steps", []) if step.get("status") == "failed"), None)
            
            if failed_step:
                error_message = failed_step.get("error", "Unknown error")
                
                if error_message not in error_groups:
                    error_groups[error_message] = {
                        "message": error_message,
                        "count": 0,
                        "tests": []
                    }
                
                error_groups[error_message]["count"] += 1
                error_groups[error_message]["tests"].append(test.get("name", "Unknown test"))
        
        # Convert groups to list and sort by count
        patterns = list(error_groups.values())
        patterns.sort(key=lambda x: x["count"], reverse=True)
        
        # If there are multiple patterns, use LLM to analyze them
        if len(patterns) > 1:
            patterns = await self._analyze_patterns_with_llm(patterns, failed_tests)
        
        return patterns
    
    async def _analyze_patterns_with_llm(self, patterns: List[Dict[str, Any]], failed_tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze failure patterns using LLM.
        
        Args:
            patterns: Initial patterns
            failed_tests: Failed tests
            
        Returns:
            Enhanced patterns
        """
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA analyst. Analyze the failure patterns in test results
        and identify common causes and potential solutions.
        """
        
        # Create a summary of patterns
        patterns_summary = ""
        for i, pattern in enumerate(patterns):
            tests_str = ", ".join(pattern["tests"][:3])
            if len(pattern["tests"]) > 3:
                tests_str += f" and {len(pattern['tests']) - 3} more"
                
            patterns_summary += f"""
            Pattern {i+1}:
            - Error Message: {pattern["message"]}
            - Count: {pattern["count"]}
            - Affected Tests: {tests_str}
            """
        
        # Create a summary of failed tests
        tests_summary = ""
        for i, test in enumerate(failed_tests[:5]):
            tests_summary += f"""
            Failed Test {i+1}: {test.get("name", "Unknown test")}
            - Description: {test.get("description", "")}
            - Failed Step: {next((step.get("action", "Unknown action") for step in test.get("steps", []) if step.get("status") == "failed"), "Unknown step")}
            - Error: {next((step.get("error", "Unknown error") for step in test.get("steps", []) if step.get("status") == "failed"), "Unknown error")}
            """
        
        if len(failed_tests) > 5:
            tests_summary += f"\nAnd {len(failed_tests) - 5} more failed tests..."
        
        prompt = f"""
        Analyze the following failure patterns and failed tests:
        
        Failure Patterns:
        {patterns_summary}
        
        Failed Tests:
        {tests_summary}
        
        Identify:
        1. Common root causes across these failures
        2. Potential solutions for each pattern
        3. Any additional patterns or insights
        """
        
        try:
            # Get completion from LLM
            response = await self.llm.get_completion(prompt, system_message)
            
            # Ask for structured output
            structured_prompt = """
            Convert your analysis into a structured JSON format with an array of pattern objects, each with:
            - pattern_name: Descriptive name for the pattern
            - error_message: The error message
            - count: How many tests have this pattern
            - root_cause: Likely root cause of the pattern
            - solution: Potential solution to address the pattern
            - tests: Array of test names affected by this pattern
            """
            
            structured_response = await self.llm.get_completion(structured_prompt)
            
            # Parse JSON response
            enhanced_patterns = ResponseParser.extract_json(structured_response)
            
            if enhanced_patterns and isinstance(enhanced_patterns, list):
                return enhanced_patterns
            elif enhanced_patterns and "patterns" in enhanced_patterns:
                return enhanced_patterns["patterns"]
            
        except Exception as e:
            logger.error(f"Error analyzing patterns with LLM: {e}")
        
        # Return original patterns if LLM analysis fails
        return patterns
    
    async def _generate_insights(self, test_results: Dict[str, Any], metrics: Dict[str, Any], failure_patterns: List[Dict[str, Any]]) -> List[str]:
        """
        Generate insights from test results.
        
        Args:
            test_results: Test results
            metrics: Test metrics
            failure_patterns: Failure patterns
            
        Returns:
            List of insights
        """
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA analyst. Generate key insights from test results,
        focusing on patterns, performance, and areas for improvement.
        """
        
        # Create a summary of metrics
        metrics_summary = "\n".join([f"- {key}: {value}" for key, value in metrics.items()])
        
        # Create a summary of failure patterns
        patterns_summary = ""
        for i, pattern in enumerate(failure_patterns):
            patterns_summary += f"""
            Pattern {i+1}: {pattern.get("pattern_name", f"Pattern {i+1}")}
            - Error: {pattern.get("error_message", pattern.get("message", "Unknown error"))}
            - Count: {pattern.get("count", 0)}
            - Root Cause: {pattern.get("root_cause", "Unknown")}
            """
        
        prompt = f"""
        Generate key insights from the following test results:
        
        Metrics:
        {metrics_summary}
        
        Failure Patterns:
        {patterns_summary}
        
        Generate 3-5 key insights about the test results, focusing on patterns,
        performance issues, and areas for improvement.
        """
        
        try:
            # Get completion from LLM
            response = await self.llm.get_completion(prompt, system_message)
            
            # Extract list of insights
            insights = ResponseParser.extract_list(response)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return ["Error generating insights"]
    
    async def _generate_recommendations(self, test_results: Dict[str, Any], failure_patterns: List[Dict[str, Any]], insights: List[str]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on test results.
        
        Args:
            test_results: Test results
            failure_patterns: Failure patterns
            insights: Test insights
            
        Returns:
            List of recommendations
        """
        # Create the prompt for the LLM
        system_message = """
        You are an expert QA consultant. Generate specific, actionable recommendations
        to improve test results based on the provided information.
        """
        
        # Create a summary of insights
        insights_summary = "\n".join([f"- {insight}" for insight in insights])
        
        # Create a summary of failure patterns
        patterns_summary = ""
        for i, pattern in enumerate(failure_patterns):
            patterns_summary += f"""
            Pattern {i+1}: {pattern.get("pattern_name", f"Pattern {i+1}")}
            - Error: {pattern.get("error_message", pattern.get("message", "Unknown error"))}
            - Count: {pattern.get("count", 0)}
            - Root Cause: {pattern.get("root_cause", "Unknown")}
            - Solution: {pattern.get("solution", "Unknown")}
            """
        
        prompt = f"""
        Generate actionable recommendations based on the following information:
        
        Insights:
        {insights_summary}
        
        Failure Patterns:
        {patterns_summary}
        
        Generate 3-5 specific, actionable recommendations to improve test results,
        addressing the key issues and grouped by category (e.g., test stability,
        test coverage, environment issues, etc.).
        
        For each recommendation, include:
        1. A clear, specific action
        2. The expected benefit
        3. Priority level (high, medium, low)
        """
        
        try:
            # Get completion from LLM
            response = await self.llm.get_completion(prompt, system_message)
            
            # Ask for structured output
            structured_prompt = """
            Convert your recommendations into a structured JSON array where each recommendation has:
            - action: The specific action to take
            - benefit: The expected benefit
            - priority: Priority level (1-5, with 5 being highest)
            - category: Category of the recommendation
            """
            
            structured_response = await self.llm.get_completion(structured_prompt)
            
            # Parse JSON response
            recommendations = ResponseParser.extract_json(structured_response)
            
            if recommendations and isinstance(recommendations, list):
                return recommendations
            elif recommendations and "recommendations" in recommendations:
                return recommendations["recommendations"]
            
            # Fallback to extracting list if JSON parsing fails
            recommendation_list = ResponseParser.extract_list(response)
            
            # Convert to list of dictionaries
            formatted_recommendations = []
            for i, rec in enumerate(recommendation_list):
                formatted_recommendations.append({
                    "id": i + 1,
                    "action": rec,
                    "priority": 3  # Default priority
                })
                
            return formatted_recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return [{
                "id": 1,
                "action": "Error generating recommendations",
                "priority": 3
            }]