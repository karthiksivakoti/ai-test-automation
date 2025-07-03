# ai-test-automation/aiqatester/analyzer/site_analyzer.py
"""
Site Analyzer module for AIQATester.

This module analyzes websites to understand their structure and functionality.
"""

from typing import Dict, List, Optional, Any
import asyncio
from urllib.parse import urljoin, urlparse
from collections import defaultdict

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
        self.max_pages = 50  # Increased from 20
        logger.info("SiteAnalyzer initialized")
    
    def _normalize_domain(self, url: str) -> str:
        """Normalize domain for comparison."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www prefix for comparison
            if domain.startswith('www.'):
                domain = domain[4:]
            # Always use https for comparison
            return f"https://{domain}"
        except Exception:
            return url
        
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
            
        logger.info(f"Starting site analysis with max_depth={self.max_depth}, max_pages={self.max_pages}")
        
        # Parse URL to get the base domain
        base_domain = self._normalize_domain(url)
        
        # Create the site model
        site_model = SiteModel(url=base_domain)
        
        # Keep track of visited and queued URLs
        visited_urls = set()
        url_queue = [(url, 0)]  # (url, depth)
        pages_per_depth = defaultdict(int)  # Track pages per depth
        
        while url_queue and len(visited_urls) < self.max_pages:
            current_url, current_depth = url_queue.pop(0)
            
            logger.info(f"Processing URL: {current_url} at depth {current_depth}")
            logger.info(f"Queue size: {len(url_queue)}, Visited: {len(visited_urls)}")
            
            # Skip if already visited
            if current_url in visited_urls:
                logger.debug(f"Skipping already visited: {current_url}")
                continue
                
            # Skip if beyond max depth
            if current_depth > self.max_depth:
                logger.debug(f"Skipping depth {current_depth} > max_depth {self.max_depth}")
                continue
            
            # Limit pages per depth to ensure we explore deeper
            if pages_per_depth[current_depth] >= 15:  # Max 15 pages per depth
                logger.info(f"Reached page limit for depth {current_depth}")
                continue
                
            logger.info(f"Analyzing page: {current_url} (depth: {current_depth})")
            
            try:
                # Navigate to the page
                await self.browser.navigate(current_url)
                
                # Extract page information
                page_model = await self._analyze_page(current_url)
                
                # Add page to site model
                site_model.add_page(page_model)
                
                # Mark as visited and increment depth counter
                visited_urls.add(current_url)
                pages_per_depth[current_depth] += 1
                
                # If not at max depth, add links to queue
                if current_depth < self.max_depth:
                    logger.info(f"Extracting links from depth {current_depth}")
                    links = await self._extract_links()
                    logger.info(f"Found {len(links)} links at depth {current_depth}")
                    
                    added_count = 0
                    # Filter links to the same domain
                    for link in links:
                        try:
                            link_url = urljoin(current_url, link)
                            link_domain = self._normalize_domain(link_url)
                            
                            # Only follow links to the same domain
                            if link_domain == base_domain and link_url not in visited_urls:
                                # Check if already in queue
                                if not any(queued_url == link_url for queued_url, _ in url_queue):
                                    url_queue.append((link_url, current_depth + 1))
                                    added_count += 1
                                    logger.debug(f"Added to queue: {link_url} at depth {current_depth + 1}")
                        except Exception as e:
                            logger.debug(f"Error processing link {link}: {e}")
                    
                    logger.info(f"Added {added_count} new links to queue for depth {current_depth + 1}")
                else:
                    logger.info(f"At max depth {self.max_depth}, not extracting more links")
            
            except Exception as e:
                logger.error(f"Error analyzing page {current_url}: {e}")
                # Still mark as visited to avoid retrying
                visited_urls.add(current_url)
                
            # Take a short break to avoid overwhelming the server
            await asyncio.sleep(1)
        
        # Build navigation map
        site_model.navigation_map = self._build_navigation_map(site_model)
        
        # Log final statistics
        for depth in range(self.max_depth + 1):
            count = pages_per_depth[depth]
            if count > 0:
                logger.info(f"Depth {depth}: {count} pages analyzed")
        
        logger.info(f"Site analysis completed for {base_domain} ({len(site_model.pages)} total pages)")
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
        
        try:
            # Get all link elements with better selectors
            link_selectors = [
                "a[href]",  # Standard links
                "[onclick*='location']",  # JavaScript redirects
                "[data-href]",  # Data attributes
                "button[formaction]"  # Form buttons with actions
            ]
            
            for selector in link_selectors:
                try:
                    link_elements = await self.browser.page.query_selector_all(selector)
                    
                    for link in link_elements:
                        href = None
                        try:
                            if selector == "a[href]":
                                href = await link.get_attribute("href")
                            elif "[onclick*='location']" in selector:
                                onclick = await link.get_attribute("onclick")
                                # Extract URL from onclick
                                import re
                                match = re.search(r"location.*?['\"]([^'\"]+)['\"]", onclick or "")
                                if match:
                                    href = match.group(1)
                            elif selector == "[data-href]":
                                href = await link.get_attribute("data-href")
                            elif selector == "button[formaction]":
                                href = await link.get_attribute("formaction")
                            
                            if href and self._is_valid_link(href):
                                links.append(href)
                                
                        except Exception as e:
                            logger.debug(f"Failed to extract link from element: {e}")
                            
                except Exception as e:
                    logger.debug(f"Failed to query selector {selector}: {e}")
            
            # Remove duplicates while preserving order
            unique_links = []
            seen = set()
            for link in links:
                if link not in seen:
                    unique_links.append(link)
                    seen.add(link)
            
            logger.debug(f"Extracted {len(unique_links)} unique links")
            return unique_links
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    def _is_valid_link(self, href: str) -> bool:
        """Check if a link is valid for crawling."""
        if not href:
            return False
            
        href_lower = href.lower()
        
        # Skip invalid protocols
        invalid_starts = [
            "javascript:", "mailto:", "tel:", "ftp:", "#",
            "data:", "blob:", "about:"
        ]
        
        for invalid in invalid_starts:
            if href_lower.startswith(invalid):
                return False
        
        # Skip file downloads
        file_extensions = [
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".zip", ".rar", ".tar", ".gz", ".exe", ".dmg", ".pkg",
            ".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico",
            ".mp3", ".mp4", ".avi", ".mov", ".wmv"
        ]
        
        for ext in file_extensions:
            if href_lower.endswith(ext):
                return False
        
        return True
    
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
