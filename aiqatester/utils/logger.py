# ai-test-automation/aiqatester/utils/logger.py
"""
Logger module for AIQATester.

This module configures logging for the application.
"""

import os
import sys
from loguru import logger

def setup_logger(log_dir: str = "logs", log_level: str = "INFO"):
    """
    Configure the logger.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level
    """
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level
    )
    
    # Add file logger
    logger.add(
        os.path.join(log_dir, "aiqatester_{time:YYYY-MM-DD}.log"),
        rotation="12:00",  # New file at noon
        retention="7 days",  # Keep logs for 7 days
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=log_level
    )
    
    logger.info("Logger configured")
    return logger

def get_logger():
    """
    Get the configured logger.
    
    Returns:
        Configured logger
    """
    return logger