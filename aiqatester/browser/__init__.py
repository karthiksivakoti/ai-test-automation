# ai-test-automation/aiqatester/browser/__init__.py
"""
Browser automation modules for AIQATester.

These modules provide browser automation capabilities.
"""

from aiqatester.browser.controller import BrowserController
from aiqatester.browser.actions import BrowserActions
from aiqatester.browser.selectors import SelectorUtils

__all__ = ['BrowserController', 'BrowserActions', 'SelectorUtils']