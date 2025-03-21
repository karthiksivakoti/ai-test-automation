# ai-test-automation/aiqatester/__init__.py
"""
AIQATester - AI-Powered Automated Testing Framework.

This package provides tools for AI-driven test generation, execution, and enhancement.
"""

__version__ = "0.1.0"

from aiqatester.director import TestDirector
from aiqatester.browser.controller import BrowserController
from aiqatester.analyzer.site_analyzer import SiteAnalyzer
from aiqatester.knowledge.site_model import SiteModel
from aiqatester.planner.strategy import TestStrategy
from aiqatester.generator.script_generator import TestScriptGenerator
from aiqatester.executor.runner import TestRunner
from aiqatester.feedback.analyzer import FeedbackAnalyzer
from aiqatester.utils.config import Config
from aiqatester.utils.logger import setup_logger

__all__ = [
    'TestDirector',
    'BrowserController',
    'SiteAnalyzer',
    'SiteModel',
    'TestStrategy',
    'TestScriptGenerator',
    'TestRunner',
    'FeedbackAnalyzer',
    'Config',
    'setup_logger'
]