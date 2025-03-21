# ai-test-automation/aiqatester/planner/coverage.py
"""
Coverage Analysis module for AIQATester.

This module analyzes test coverage and identifies gaps.
"""

from typing import Dict, List, Any

from loguru import logger

from aiqatester.knowledge.site_model import SiteModel

class CoverageAnalyzer:
    """Analyzes test coverage and identifies gaps."""
    
    def __init__(self, site_model: SiteModel):
        """
        Initialize the coverage analyzer.
        
        Args:
            site_model: Site model containing website information
        """
        self.site_model = site_model
        logger.info("CoverageAnalyzer initialized")
        
    def analyze_coverage(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze test coverage and identify gaps.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            Coverage analysis results
        """
        logger.info(f"Analyzing coverage for {len(test_cases)} test cases")
        
        # Extract coverage data
        page_coverage = self._analyze_page_coverage(test_cases)
        flow_coverage = self._analyze_flow_coverage(test_cases)
        element_coverage = self._analyze_element_coverage(test_cases)
        
        # Calculate overall coverage percentage
        total_items = len(self.site_model.pages) + len(self.site_model.business_flows)
        covered_items = len(page_coverage['covered_pages']) + len(flow_coverage['covered_flows'])
        
        if total_items > 0:
            coverage_percentage = (covered_items / total_items) * 100
        else:
            coverage_percentage = 0
        
        # Identify gaps
        coverage_gaps = []
        
        # Add uncovered pages
        for page_url in page_coverage['uncovered_pages']:
            page = self.site_model.get_page(page_url)
            if page and page.title:
                coverage_gaps.append(f"Page not covered: {page.title} ({page_url})")
            else:
                coverage_gaps.append(f"Page not covered: {page_url}")
        
        # Add uncovered flows
        for flow in flow_coverage['uncovered_flows']:
            coverage_gaps.append(f"Business flow not covered: {flow.get('name', 'Unnamed flow')}")
        
        # Return coverage analysis
        return {
            'coverage_percentage': round(coverage_percentage, 2),
            'page_coverage': page_coverage,
            'flow_coverage': flow_coverage,
            'element_coverage': element_coverage,
            'coverage_gaps': coverage_gaps
        }
    
    def _analyze_page_coverage(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze page coverage.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            Page coverage analysis
        """
        covered_pages = set()
        
        # Extract page URLs from test cases
        for test_case in test_cases:
            # Check steps for page URLs
            for step in test_case.get('steps', []):
                page_url = step.get('page_url')
                if page_url and page_url in self.site_model.pages:
                    covered_pages.add(page_url)
        
        # Determine uncovered pages
        all_pages = set(self.site_model.pages.keys())
        uncovered_pages = all_pages - covered_pages
        
        return {
            'covered_pages': list(covered_pages),
            'uncovered_pages': list(uncovered_pages),
            'coverage_percentage': round((len(covered_pages) / len(all_pages)) * 100, 2) if all_pages else 0
        }
    
    def _analyze_flow_coverage(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze business flow coverage.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            Flow coverage analysis
        """
        covered_flows = []
        uncovered_flows = []
        
        # Extract covered flows from test cases
        for test_case in test_cases:
            flow_name = test_case.get('business_flow')
            if flow_name:
                covered_flows.append(flow_name)
        
        # Convert to set to remove duplicates
        covered_flow_names = set(covered_flows)
        
        # Determine uncovered flows
        for flow in self.site_model.business_flows:
            flow_name = flow.get('name')
            if flow_name and flow_name not in covered_flow_names:
                uncovered_flows.append(flow)
        
        flow_count = len(self.site_model.business_flows)
        
        return {
            'covered_flows': list(covered_flow_names),
            'uncovered_flows': uncovered_flows,
            'coverage_percentage': round((len(covered_flow_names) / flow_count) * 100, 2) if flow_count else 0
        }
    
    def _analyze_element_coverage(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze interactive element coverage.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            Element coverage analysis
        """
        covered_elements = set()
        
        # Extract selectors from test cases
        for test_case in test_cases:
            for step in test_case.get('steps', []):
                selector = step.get('element')
                if selector:
                    covered_elements.add(selector)
        
        # Count total elements across all pages
        all_elements = set()
        for page in self.site_model.pages.values():
            for element_type, elements in page.interactive_elements.items():
                for element in elements:
                    # Create a unique identifier for the element
                    element_id = element.get('id')
                    element_class = element.get('class')
                    element_text = element.get('text')
                    
                    if element_id:
                        all_elements.add(f"#{element_id}")
                    elif element_class:
                        all_elements.add(f".{element_class}")
                    elif element_text:
                        all_elements.add(f"{element_type}[text='{element_text}']")
        
        return {
            'covered_elements': list(covered_elements),
            'total_elements': len(all_elements),
            'coverage_percentage': round((len(covered_elements) / len(all_elements)) * 100, 2) if all_elements else 0
        }