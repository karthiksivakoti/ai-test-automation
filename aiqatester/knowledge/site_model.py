# ai-test-automation/aiqatester/knowledge/site_model.py
"""
Site Model module for AIQATester.

This module defines the data structure for storing website information.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import datetime

@dataclass
class PageModel:
    """Model for a single page in a website."""
    url: str
    title: Optional[str] = None
    interactive_elements: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    content_summary: Optional[str] = None
    
@dataclass
class SiteModel:
    """Model for a complete website."""
    url: str
    pages: Dict[str, PageModel] = field(default_factory=dict)
    navigation_map: Dict[str, List[str]] = field(default_factory=dict)
    business_flows: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    
    def add_page(self, page: PageModel) -> None:
        """Add a page to the site model."""
        self.pages[page.url] = page
    
    def get_page(self, url: str) -> Optional[PageModel]:
        """Get a page by URL."""
        return self.pages.get(url)
    
    def add_business_flow(self, flow: Dict[str, Any]) -> None:
        """Add a business flow to the site model."""
        self.business_flows.append(flow)
    
    def get_business_flows(self) -> List[Dict[str, Any]]:
        """Get all business flows."""
        return self.business_flows
    
    def get_page_count(self) -> int:
        """Get the number of pages in the site model."""
        return len(self.pages)
    
    def get_interactive_element_count(self) -> Dict[str, int]:
        """Get the count of interactive elements by type."""
        counts = {}
        
        for page in self.pages.values():
            for element_type, elements in page.interactive_elements.items():
                if element_type not in counts:
                    counts[element_type] = 0
                counts[element_type] += len(elements)
        
        return counts
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the site model to a dictionary."""
        return {
            "url": self.url,
            "pages": {url: {
                "url": page.url,
                "title": page.title,
                "content_summary": page.content_summary,
                "interactive_elements": page.interactive_elements
            } for url, page in self.pages.items()},
            "navigation_map": self.navigation_map,
            "business_flows": self.business_flows,
            "created_at": self.created_at.isoformat()
        }