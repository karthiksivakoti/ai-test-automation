# ai-test-automation/aiqatester/utils/exceptions.py
"""
Exceptions module for AIQATester.

This module defines custom exceptions.
"""

class AIQATesterError(Exception):
    """Base exception for AIQATester."""
    pass

class BrowserError(AIQATesterError):
    """Exception raised when a browser operation fails."""
    pass

class LLMError(AIQATesterError):
    """Exception raised when an LLM operation fails."""
    pass

class TestExecutionError(AIQATesterError):
    """Exception raised when test execution fails."""
    pass

class ConfigurationError(AIQATesterError):
    """Exception raised when configuration is invalid."""
    pass

class DataError(AIQATesterError):
    """Exception raised when there's an issue with test data."""
    pass

class ElementNotFoundError(BrowserError):
    """Exception raised when an element is not found."""
    pass

class NavigationError(BrowserError):
    """Exception raised when navigation fails."""
    pass

class TimeoutError(BrowserError):
    """Exception raised when an operation times out."""
    pass

class AssertionError(TestExecutionError):
    """Exception raised when a test assertion fails."""
    pass

class ScriptGenerationError(AIQATesterError):
    """Exception raised when script generation fails."""
    pass