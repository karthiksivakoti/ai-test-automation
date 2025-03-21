# ai-test-automation/aiqatester/knowledge/__init__.py
"""
Knowledge base modules for AIQATester.

These modules store and manage information about websites,
business flows, and testing patterns.
"""

from aiqatester.knowledge.site_model import SiteModel, PageModel
from aiqatester.knowledge.business_flows import BusinessFlow, Step
from aiqatester.knowledge.test_patterns import (
    get_test_patterns_for_element,
    get_test_patterns_for_flow,
    get_test_data_generator,
    get_assertion
)

__all__ = [
    'SiteModel', 'PageModel', 'BusinessFlow', 'Step',
    'get_test_patterns_for_element', 'get_test_patterns_for_flow',
    'get_test_data_generator', 'get_assertion'
]