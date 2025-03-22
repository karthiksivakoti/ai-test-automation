# Create a new file: aiqatester/utils/data_exporter.py

import json
import os
import datetime
from typing import Dict, Any, List, Optional

class DataExporter:
    """Export intermediate data from test execution process."""
    
    def __init__(self, export_dir: str = "exports"):
        """Initialize the data exporter."""
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        
        # Create a timestamp for this run
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = os.path.join(export_dir, f"run_{self.timestamp}")
        os.makedirs(self.run_dir, exist_ok=True)
    
    def export_site_model(self, site_model: Any) -> str:
        """Export site model data to a JSON file."""
        data = {
            "url": site_model.url,
            "pages": {
                url: {
                    "url": page.url,
                    "title": page.title,
                    "content_summary": page.content_summary[:1000] + "..." if page.content_summary and len(page.content_summary) > 1000 else page.content_summary,
                    "interactive_elements": {
                        element_type: len(elements) 
                        for element_type, elements in page.interactive_elements.items()
                    },
                    "element_samples": {
                        element_type: elements[:10] if elements else []
                        for element_type, elements in page.interactive_elements.items()
                    }
                }
                for url, page in site_model.pages.items()
            },
            "business_flows": site_model.business_flows
        }
        
        # Save to file
        filepath = os.path.join(self.run_dir, "site_model.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
            
        return filepath
    
    def export_test_strategy(self, test_strategy: Dict[str, Any]) -> str:
        """Export test strategy to a JSON file."""
        filepath = os.path.join(self.run_dir, "test_strategy.json")
        with open(filepath, "w") as f:
            json.dump(test_strategy, f, indent=2)
            
        return filepath
    
    def export_test_scripts(self, test_scripts: List[Dict[str, Any]]) -> str:
        """Export test scripts to a JSON file."""
        filepath = os.path.join(self.run_dir, "test_scripts.json")
        with open(filepath, "w") as f:
            json.dump(test_scripts, f, indent=2)
            
        return filepath
    
    def export_test_results(self, test_results: Dict[str, Any]) -> str:
        """Export test results to a JSON file."""
        filepath = os.path.join(self.run_dir, "test_results.json")
        with open(filepath, "w") as f:
            json.dump(test_results, f, indent=2)
            
        return filepath