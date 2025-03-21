# ai-test-automation/tests/test_generator.py
"""
Tests for the test script generator module.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch

from aiqatester.generator.script_generator import TestScriptGenerator
from aiqatester.knowledge.site_model import SiteModel
from aiqatester.llm.openai_client import OpenAIClient

@pytest.mark.asyncio
async def test_script_generator_initialization():
    """Test that the script generator initializes correctly."""
    site_model_mock = MagicMock(spec=SiteModel)
    llm_mock = MagicMock(spec=OpenAIClient)
    generator = TestScriptGenerator(site_model_mock, llm_mock)
    assert generator.site_model == site_model_mock
    assert generator.llm == llm_mock

@pytest.mark.asyncio
async def test_generate_scripts():
    """Test that generate_scripts method works correctly."""
    # Create mocks
    site_model_mock = MagicMock(spec=SiteModel)
    llm_mock = MagicMock(spec=OpenAIClient)
    
    # Setup LLM mock behavior
    async def mock_get_completion(prompt, system_message=None):
        return '{"name": "Test Script", "steps": [{"step": 1, "action": "Click button", "selector": "#button"}]}'
    
    llm_mock.get_completion = mock_get_completion
    
    # Create generator with mocks
    generator = TestScriptGenerator(site_model_mock, llm_mock)
    
    # Create test strategy
    test_strategy = {
        "test_cases": [
            {
                "name": "Test Case 1",
                "description": "Test case description",
                "priority": 3,
                "steps": ["Step 1", "Step 2"]
            }
        ]
    }
    
    # Call generate_scripts
    scripts = await generator.generate_scripts(test_strategy)
    
    # Check result
    assert scripts is not None
    assert len(scripts) == 1
    assert scripts[0]["name"] == "Test Script"
    assert "steps" in scripts[0]
    assert len(scripts[0]["steps"]) == 1

@pytest.mark.asyncio
async def test_generate_test_script():
    """Test that _generate_test_script method works correctly."""
    # Create mocks
    site_model_mock = MagicMock(spec=SiteModel)
    llm_mock = MagicMock(spec=OpenAIClient)
    
    # Setup site model mock behavior
    site_model_mock.pages = {
        "https://example.com": MagicMock(
            title="Example Page",
            interactive_elements={
                "links": [{"text": "Link 1", "href": "/page1"}],
                "buttons": [{"text": "Button 1"}]
            }
        )
    }
    
    # Setup LLM mock behavior
    async def mock_get_completion(prompt, system_message=None):
        return '{"name": "Test Script", "steps": [{"step": 1, "action": "Click button", "selector": "#button"}]}'
    
    llm_mock.get_completion = mock_get_completion
    
    # Create generator with mocks
    generator = TestScriptGenerator(site_model_mock, llm_mock)
    
    # Create test case
    test_case = {
        "name": "Test Case 1",
        "description": "Test case description",
        "priority": 3,
        "steps": ["Step 1", "Step 2"]
    }
    
    # Call _generate_test_script
    script = await generator._generate_test_script(test_case)
    
    # Check result
    assert script is not None
    assert script["name"] == "Test Script"
    assert "steps" in script
    assert len(script["steps"]) == 1