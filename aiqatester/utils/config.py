# ai-test-automation/aiqatester/utils/config.py
"""
Configuration module for AIQATester.

This module manages configuration settings.
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    """Configuration settings for AIQATester."""
    
    # Browser settings
    headless: bool = True
    browser_type: str = "chromium"
    slow_mo: int = 50
    viewport_width: int = 1280
    viewport_height: int = 720
    timeout: int = 30000
    
    # LLM settings
    llm_provider: str = "openai"
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-3-opus-20240229"
    
    # Directories
    screenshot_dir: str = "screenshots"
    log_dir: str = "logs"
    report_dir: str = "reports"
    
    # Testing settings
    max_depth: int = 3
    max_test_cases: int = 10
    max_pages: int = 20
    
    def __post_init__(self):
        # Override settings from environment variables
        self._override_from_env()
    
    def _override_from_env(self):
        """Override settings from environment variables."""
        # Browser settings
        if "HEADLESS" in os.environ:
            self.headless = os.environ["HEADLESS"].lower() in ("true", "1", "yes")
        
        if "BROWSER_TYPE" in os.environ:
            self.browser_type = os.environ["BROWSER_TYPE"]
        
        if "SLOW_MO" in os.environ:
            self.slow_mo = int(os.environ["SLOW_MO"])
        
        if "VIEWPORT_WIDTH" in os.environ:
            self.viewport_width = int(os.environ["VIEWPORT_WIDTH"])
        
        if "VIEWPORT_HEIGHT" in os.environ:
            self.viewport_height = int(os.environ["VIEWPORT_HEIGHT"])
        
        if "TIMEOUT" in os.environ:
            self.timeout = int(os.environ["TIMEOUT"])
        
        # LLM settings
        if "LLM_PROVIDER" in os.environ:
            self.llm_provider = os.environ["LLM_PROVIDER"]
        
        if "OPENAI_MODEL" in os.environ:
            self.openai_model = os.environ["OPENAI_MODEL"]
        
        if "ANTHROPIC_MODEL" in os.environ:
            self.anthropic_model = os.environ["ANTHROPIC_MODEL"]
        
        # Directories
        if "SCREENSHOT_DIR" in os.environ:
            self.screenshot_dir = os.environ["SCREENSHOT_DIR"]
        
        if "LOG_DIR" in os.environ:
            self.log_dir = os.environ["LOG_DIR"]
        
        if "REPORT_DIR" in os.environ:
            self.report_dir = os.environ["REPORT_DIR"]
        
        # Testing settings
        if "MAX_DEPTH" in os.environ:
            self.max_depth = int(os.environ["MAX_DEPTH"])
        
        if "MAX_TEST_CASES" in os.environ:
            self.max_test_cases = int(os.environ["MAX_TEST_CASES"])
        
        if "MAX_PAGES" in os.environ:
            self.max_pages = int(os.environ["MAX_PAGES"])
    
    @classmethod
    def from_file(cls, file_path: str) -> "Config":
        """
        Load configuration from a YAML file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Config object
        """
        with open(file_path, "r") as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.
        
        Returns:
            Configuration as a dictionary
        """
        return {
            "headless": self.headless,
            "browser_type": self.browser_type,
            "slow_mo": self.slow_mo,
            "viewport_width": self.viewport_width,
            "viewport_height": self.viewport_height,
            "timeout": self.timeout,
            "llm_provider": self.llm_provider,
            "openai_model": self.openai_model,
            "anthropic_model": self.anthropic_model,
            "screenshot_dir": self.screenshot_dir,
            "log_dir": self.log_dir,
            "report_dir": self.report_dir,
            "max_depth": self.max_depth,
            "max_test_cases": self.max_test_cases,
            "max_pages": self.max_pages
        }
    
    def save_to_file(self, file_path: str) -> None:
        """
        Save configuration to a YAML file.
        
        Args:
            file_path: Path to save the configuration to
        """
        with open(file_path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)