# ai-test-automation/tests/test_analyzer.py
"""
Tests for the website analyzer module.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch

from aiqatester.analyzer.site_analyzer import SiteAnalyzer
from aiqatester.browser.controller import BrowserController

@pytest.mark.asyncio
async def test_site_analyzer_initialization():
    """Test that the site analyzer initializes correctly."""
    browser_mock = MagicMock(spec=BrowserController)
    analyzer = SiteAnalyzer(browser_mock)
    assert analyzer.browser == browser_mock

@pytest.mark.asyncio
async def test_analyze_site():
    """Test that analyze_site method works correctly."""
    # Create mocks
    browser_mock = MagicMock(spec=BrowserController)
    
    # Setup browser mock behavior
    async def mock_navigate(url):
        return True
    
    async def mock_get_page_text():
        return "This is a test page content"
    
    async def mock_extract_interactive_elements():
        return {
            "links": [{"text": "Link 1", "href": "/page1"}],
            "buttons": [{"text": "Button 1"}]
        }
    
    browser_mock.navigate = mock_navigate
    browser_mock.get_page_text = mock_get_page_text
    browser_mock.extract_interactive_elements = mock_extract_interactive_elements
    
    # Create analyzer with mock
    analyzer = SiteAnalyzer(browser_mock)
    
    # Set low values for testing
    analyzer.max_depth = 1
    analyzer.max_pages = 1
    
    # Call analyze_site
    site_model = await analyzer.analyze_site("https://example.com")
    
    # Check result
    assert site_model is not None
    assert site_model.url == "https://example.com"
    assert len(site_model.pages) > 0

@pytest.mark.asyncio
async def test_analyze_page():
    """Test that _analyze_page method works correctly."""
    # Create mocks
    browser_mock = MagicMock(spec=BrowserController)
    
    # Setup browser mock behavior
    async def mock_get_element_by_selector(selector):
        element_mock = MagicMock()
        async def mock_text_content():
            return "Test Page"
        element_mock.text_content = mock_text_content
        return element_mock
    
    async def mock_extract_interactive_elements():
        return {
            "links": [{"text": "Link 1", "href": "/page1"}],
            "buttons": [{"text": "Button 1"}]
        }
    
    async def mock_get_page_text():
        return "This is a test page content"
    
    browser_mock.get_element_by_selector = mock_get_element_by_selector
    browser_mock.extract_interactive_elements = mock_extract_interactive_elements
    browser_mock.get_page_text = mock_get_page_text
    
    # Create analyzer with mock
    analyzer = SiteAnalyzer(browser_mock)
    
    # Call _analyze_page
    page_model = await analyzer._analyze_page("https://example.com")
    
    # Check result
    assert page_model is not None
    assert page_model.url == "https://example.com"
    assert page_model.title == "Test Page"
    assert "links" in page_model.interactive_elements
    assert "buttons" in page_model.interactive_elements