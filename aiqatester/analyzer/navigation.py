# ai-test-automation/aiqatester/analyzer/navigation.py
"""
Navigation Analyzer module for AIQATester.

This module analyzes website navigation and page transitions.
"""

from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

from loguru import logger

from aiqatester.browser.controller import BrowserController
from aiqatester.knowledge.site_model import SiteModel

class NavigationAnalyzer:
    """Analyzes website navigation and page transitions."""
    
    def __init__(self, browser_controller: BrowserController):
        """
        Initialize the navigation analyzer.
        
        Args:
            browser_controller: Browser controller instance
        """
        self.browser = browser_controller
        logger.info("NavigationAnalyzer initialized")
        
    async def map_site_navigation(self, start_url: str, max_depth: int = 3) -> Dict[str, Any]:
        """
        Map the navigation structure of a website.
        
        Args:
            start_url: The starting URL
            max_depth: Maximum depth to crawl
            
        Returns:
            Navigation map of the website
        """
        # Parse URL to get the base domain
        parsed_url = urlparse(start_url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Keep track of visited pages and their links
        navigation_map = {}
        visited_urls = set()
        url_queue = [(start_url, 0)]  # (url, depth)
        
        while url_queue:
            current_url, current_depth = url_queue.pop(0)
            
            # Skip if already visited or beyond max depth
            if current_url in visited_urls or current_depth > max_depth:
                continue
                
            logger.info(f"Mapping navigation for: {current_url} (depth: {current_depth})")
            
            try:
                # Navigate to the page
                await self.browser.navigate(current_url)
                
                # Extract links
                links = await self._extract_links()
                navigation_map[current_url] = []
                
                # Process links
                for link in links:
                    # Convert to absolute URL
                    absolute_url = urljoin(current_url, link)
                    parsed_link = urlparse(absolute_url)
                    
                    # Skip fragment identifiers (same page)
                    if parsed_link.fragment and parsed_link._replace(fragment='').geturl() == current_url:
                        continue
                    
                    # Only include links to the same domain
                    link_domain = f"{parsed_link.scheme}://{parsed_link.netloc}"
                    if link_domain == base_domain:
                        navigation_map[current_url].append(absolute_url)
                        
                        # Add to queue if not visited
                        if absolute_url not in visited_urls:
                            url_queue.append((absolute_url, current_depth + 1))
                
                # Mark as visited
                visited_urls.add(current_url)
                
            except Exception as e:
                logger.error(f"Error mapping navigation for {current_url}: {e}")
                navigation_map[current_url] = []
        
        return {
            "base_domain": base_domain,
            "pages": list(visited_urls),
            "navigation_map": navigation_map
        }
    
    async def _extract_links(self) -> List[str]:
        """
        Extract links from the current page.
        
        Returns:
            List of link URLs
        """
        links = []
        
        # Get all link elements
        link_elements = await self.browser.page.query_selector_all("a[href]")
        
        for link in link_elements:
            try:
                href = await link.get_attribute("href")
                if href and not href.startswith("javascript:") and not href.startswith("#"):
                    links.append(href)
            except Exception as e:
                logger.debug(f"Failed to extract link: {e}")
        
        return links
    
    async def analyze_navigation_flow(self, flow_urls: List[str]) -> Dict[str, Any]:
        """
        Analyze a specific navigation flow.
        
        Args:
            flow_urls: List of URLs in the flow
            
        Returns:
            Flow analysis results
        """
        flow_results = {
            "steps": [],
            "successful": True,
            "issues": []
        }
        
        for i, url in enumerate(flow_urls):
            try:
                logger.info(f"Navigating to step {i+1}: {url}")
                
                # Navigate to the URL
                await self.browser.navigate(url)
                
                # Take a screenshot
                screenshot = await self.browser.take_screenshot(f"flow_step_{i+1}")
                
                # Check page loading
                title = await self.browser.page.title()
                
                flow_results["steps"].append({
                    "step": i + 1,
                    "url": url,
                    "title": title,
                    "screenshot": screenshot,
                    "successful": True
                })
                
            except Exception as e:
                logger.error(f"Error in navigation flow at step {i+1}: {e}")
                
                flow_results["steps"].append({
                    "step": i + 1,
                    "url": url,
                    "title": None,
                    "screenshot": None,
                    "successful": False,
                    "error": str(e)
                })
                
                flow_results["successful"] = False
                flow_results["issues"].append(f"Step {i+1} failed: {str(e)}")
                break
        
        return flow_results
    
    async def identify_navigation_patterns(self, site_model: SiteModel) -> Dict[str, Any]:
        """
        Identify common navigation patterns in the site.
        
        Args:
            site_model: Site model
            
        Returns:
            Identified navigation patterns
        """
        patterns = {
            "menu_navigation": [],
            "breadcrumb_navigation": [],
            "pagination": [],
            "search_navigation": []
        }
        
        # Check each page for navigation elements
        for url, page in site_model.pages.items():
            try:
                # Navigate to the page
                await self.browser.navigate(url)
                
                # Check for navigation menus
                menu_elements = await self.browser.page.query_selector_all("nav, .nav, .menu, .navigation, header ul")
                if menu_elements:
                    patterns["menu_navigation"].append(url)
                
                # Check for breadcrumbs
                breadcrumb_elements = await self.browser.page.query_selector_all(".breadcrumb, .breadcrumbs, ol.breadcrumb, nav[aria-label='breadcrumb']")
                if breadcrumb_elements:
                    patterns["breadcrumb_navigation"].append(url)
                
                # Check for pagination
                pagination_elements = await self.browser.page.query_selector_all(".pagination, ul.pagination, .pager, .pages")
                if pagination_elements:
                    patterns["pagination"].append(url)
                
                # Check for search functionality
                search_elements = await self.browser.page.query_selector_all("form[role='search'], input[type='search'], .search-form, [name='q'], [name='search']")
                if search_elements:
                    patterns["search_navigation"].append(url)
                
            except Exception as e:
                logger.error(f"Error identifying navigation patterns for {url}: {e}")
        
        return patterns