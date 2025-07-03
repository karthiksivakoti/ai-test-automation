# ai-test-automation/aiqatester/analyzer/site_analyzer.py
"""
Site Analyzer module for AIQATester.

This module analyzes websites to understand their structure and functionality.
"""

from typing import Dict, List, Optional, Any
import asyncio
from urllib.parse import urljoin, urlparse

from loguru import logger
from bs4 import BeautifulSoup

from aiqatester.browser.controller import BrowserController
from aiqatester.analyzer.element_finder import ElementFinder
from aiqatester.knowledge.site_model import SiteModel, PageModel

class SiteAnalyzer:
    """Analyzes website structure and functionality."""
    
    def __init__(self, browser_controller: BrowserController):
        """
        Initialize the site analyzer.
        
        Args:
            browser_controller: Browser controller instance
        """
        self.browser = browser_controller
        self.element_finder = ElementFinder(browser_controller)
        self.max_depth = 3  # Default max depth for crawling
        self.max_pages = 20  # Default max pages to analyze
        logger.info("SiteAnalyzer initialized")
        
    async def analyze_site(self, url: str, max_depth: int = None, max_pages: int = None) -> SiteModel:
        """
        Analyze a website and build a site model.
        
        Args:
            url: The website URL to analyze
            max_depth: Maximum depth for crawling (default: self.max_depth)
            max_pages: Maximum pages to analyze (default: self.max_pages)
            
        Returns:
            SiteModel containing website information
        """
        if max_depth is not None:
            self.max_depth = max_depth
            
        if max_pages is not None:
            self.max_pages = max_pages
            
        # Parse URL to get the base domain
        parsed_url = urlparse(url)
        base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # Create the site model
        site_model = SiteModel(url=base_domain)
        
        # Keep track of visited and queued URLs
        visited_urls = set()
        url_queue = [(url, 0)]  # (url, depth)
        
        while url_queue and len(visited_urls) < self.max_pages:
            current_url, current_depth = url_queue.pop(0)
            
            # Skip if already visited or beyond max depth
            if current_url in visited_urls or current_depth >= self.max_depth:
                continue
                
            logger.info(f"Analyzing page: {current_url} (depth: {current_depth})")
            
            try:
                # Navigate to the page
                await self.browser.navigate(current_url)
                
                # Extract page information
                page_model = await self._analyze_page(current_url)
                
                # Add page to site model
                site_model.add_page(page_model)
                
                # Mark as visited
                visited_urls.add(current_url)
                
                # If not at max depth, add links to queue
                if current_depth < self.max_depth:
                    links = await self._extract_links()
                    
                    # Filter links to the same domain
                    for link in links:
                        link_url = urljoin(current_url, link)
                        parsed_link = urlparse(link_url)
                        link_domain = f"{parsed_link.scheme}://{parsed_link.netloc}"
                        
                        # Only follow links to the same domain
                        if link_domain == base_domain and link_url not in visited_urls:
                            url_queue.append((link_url, current_depth + 1))
            
            except Exception as e:
                logger.error(f"Error analyzing page {current_url}: {e}")
                
            # Take a short break to avoid overwhelming the server
            await asyncio.sleep(1)
        
        # Build navigation map
        site_model.navigation_map = self._build_navigation_map(site_model)
        
        logger.info(f"Site analysis completed for {base_domain} ({len(site_model.pages)} pages)")
        return site_model
    
    async def _analyze_page(self, url: str) -> PageModel:
        """
        Analyze a single page and create a page model.
        
        Args:
            url: URL of the page to analyze
            
        Returns:
            PageModel containing page information
        """
        # Get page title
        title_element = await self.browser.get_element_by_selector("title")
        title = await title_element.text_content() if title_element else "Untitled Page"
        
        # Extract interactive elements
        interactive_elements = await self.browser.extract_interactive_elements()
        
        # Get page text for content summary
        page_text = await self.browser.get_page_text()
        content_summary = page_text[:500] + "..." if len(page_text) > 500 else page_text
        
        # Create page model
        page_model = PageModel(
            url=url,
            title=title,
            interactive_elements=interactive_elements,
            content_summary=content_summary
        )
        
        return page_model
    
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
    
    def _build_navigation_map(self, site_model: SiteModel) -> Dict[str, List[str]]:
        """
        Build a navigation map from the analyzed pages.
        
        Args:
            site_model: The site model
            
        Returns:
            Navigation map (dictionary of URL to list of linked URLs)
        """
        navigation_map = {}
        
        for page_url, page in site_model.pages.items():
            # Get all links from this page
            outgoing_links = []
            
            for link in page.interactive_elements.get("links", []):
                href = link.get("href", "")
                if href:
                    # Make absolute URL
                    absolute_url = urljoin(page_url, href)
                    
                    # Only include links to other pages in the site model
                    if absolute_url in site_model.pages:
                        outgoing_links.append(absolute_url)
            
            navigation_map[page_url] = outgoing_links
        
        return navigation_map
