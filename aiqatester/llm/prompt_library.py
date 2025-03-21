# ai-test-automation/aiqatester/llm/prompt_library.py
"""
Prompt Library module for AIQATester.

This module provides prompt templates for various LLM tasks.
"""

from typing import Dict, Any

# Prompt templates for site analysis
SITE_ANALYSIS_PROMPTS = {
    "business_understanding": """
You are an expert QA tester with deep understanding of web applications. 
Analyze the provided HTML content from a website and identify:

1. What is the business purpose of this website?
2. What are the key user flows and business operations?
3. What critical functionality should be tested?
4. What common user interactions occur on this site?

Be specific and thorough in your analysis.

HTML Content:
{html_content}
""",
    
    "element_classification": """
Analyze the interactive elements found on this webpage and classify them based on their 
functionality. For each element, determine:

1. What user action it enables (e.g., navigation, form submission, filtering)
2. Its importance to core business flows (high, medium, low)
3. Potential edge cases to test

Elements:
{elements_json}
"""
}

# Prompt templates for test generation
TEST_GENERATION_PROMPTS = {
    "business_flow_tests": """
Create test cases for the following business flow:

Flow Name: {flow_name}
Flow Description: {flow_description}

For each test case, include:
1. Test name
2. Test description
3. Preconditions
4. Test steps (detailed with exact elements to interact with)
5. Expected results
6. Priority (critical, high, medium, low)

Create both happy path tests and appropriate edge cases.
""",
    
    "test_script_generation": """
Convert the following test case into an executable test script:

Test Case:
{test_case_json}

The script should include:
1. Detailed browser actions with exact selectors
2. Input data values
3. Explicit wait conditions
4. Verification points
5. Error handling

Format the response as a JSON object with steps that can be executed programmatically.
"""
}

# Prompt templates for test enhancement
TEST_ENHANCEMENT_PROMPTS = {
    "failure_analysis": """
Analyze the following test failure and provide insights:

Test Script:
{test_script_json}

Test Results:
{test_results_json}

Screenshots:
{screenshot_descriptions}

Provide:
1. Root cause analysis
2. Suggested fixes
3. Recommendations for test improvement
"""
}

# Prompt templates for data generation
DATA_GENERATION_PROMPTS = {
    "test_data": """
Generate test data for the following test case:

Test Case:
{test_case_json}

Data Requirements:
{data_requirements}

Generate:
1. Valid test data for happy path testing
2. Invalid test data for negative testing
3. Edge case data for boundary testing

Format the response as a JSON object with test data values.
"""
}

# Prompt templates for accessibility testing
ACCESSIBILITY_TESTING_PROMPTS = {
    "accessibility_evaluation": """
Evaluate the accessibility of the following webpage content:

HTML Content:
{html_content}

Interactive Elements:
{elements_json}

Evaluate:
1. Keyboard navigability
2. Screen reader compatibility
3. Color contrast issues
4. Form label associations
5. ARIA attribute usage

Format the response as a JSON object with accessibility issues and recommendations.
"""
}

def get_prompt(prompt_type: str, prompt_name: str, **kwargs) -> str:
    """
    Get a prompt template with variables filled in.
    
    Args:
        prompt_type: Type of prompt (e.g., 'site_analysis', 'test_generation')
        prompt_name: Name of the prompt template
        **kwargs: Variables to fill in the prompt template
        
    Returns:
        Formatted prompt
    """
    # Get the appropriate prompt dictionary
    if prompt_type == "site_analysis":
        prompts = SITE_ANALYSIS_PROMPTS
    elif prompt_type == "test_generation":
        prompts = TEST_GENERATION_PROMPTS
    elif prompt_type == "test_enhancement":
        prompts = TEST_ENHANCEMENT_PROMPTS
    elif prompt_type == "data_generation":
        prompts = DATA_GENERATION_PROMPTS
    elif prompt_type == "accessibility_testing":
        prompts = ACCESSIBILITY_TESTING_PROMPTS
    else:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    
    # Get the prompt template
    template = prompts.get(prompt_name)
    if not template:
        raise ValueError(f"Unknown prompt name: {prompt_name}")
    
    # Fill in the variables
    return template.format(**kwargs)