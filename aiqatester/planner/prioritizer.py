# ai-test-automation/aiqatester/planner/prioritizer.py
"""
Test Prioritizer module for AIQATester.

This module prioritizes test cases based on importance and impact.
"""

from typing import Dict, List, Any

from loguru import logger

class TestPrioritizer:
    """Prioritizes test cases based on importance and impact."""
    
    def __init__(self):
        """Initialize the test prioritizer."""
        logger.info("TestPrioritizer initialized")
        
    def prioritize_tests(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prioritize test cases.
        
        Args:
            test_cases: List of test cases to prioritize
            
        Returns:
            Prioritized list of test cases
        """
        # Make a copy to avoid modifying the original
        prioritized = test_cases.copy()
        
        # Ensure all test cases have a priority field
        for test_case in prioritized:
            if 'priority' not in test_case:
                test_case['priority'] = self._calculate_priority(test_case)
        
        # Sort by priority (higher values first)
        prioritized.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        logger.info(f"Prioritized {len(test_cases)} test cases")
        return prioritized
    
    def _calculate_priority(self, test_case: Dict[str, Any]) -> int:
        """
        Calculate priority for a test case if not explicitly specified.
        
        Args:
            test_case: Test case information
            
        Returns:
            Priority value (1-5)
        """
        # Default priority
        default_priority = 3
        
        # Look for priority keywords in the test case name and description
        name = test_case.get('name', '').lower()
        description = test_case.get('description', '').lower()
        text = name + ' ' + description
        
        # Check for priority indicators
        if any(kw in text for kw in ['critical', 'crucial', 'essential', 'must-have']):
            return 5
        elif any(kw in text for kw in ['high', 'important', 'major']):
            return 4
        elif any(kw in text for kw in ['medium', 'moderate', 'average']):
            return 3
        elif any(kw in text for kw in ['low', 'minor', 'nice-to-have']):
            return 2
        elif any(kw in text for kw in ['trivial', 'cosmetic']):
            return 1
        
        # Check for business flow importance
        category = test_case.get('category', '').lower()
        if 'core' in category or 'business' in category:
            return 4
        
        # Check for test type
        if 'smoke' in text or 'sanity' in text:
            return 5
        elif 'regression' in text:
            return 4
        elif 'edge' in text or 'boundary' in text:
            return 3
        
        return default_priority