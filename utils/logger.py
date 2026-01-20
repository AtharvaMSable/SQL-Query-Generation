"""
Logging Configuration Module
Sets up application-wide logging with proper formatting and handlers.
"""

import logging
import sys
from datetime import datetime
from config.settings import settings


def setup_logger(name: str = 'askql', level: str = None) -> logging.Logger:
    """
    Set up a configured logger instance.
    
    Args:
        name: Logger name (defaults to 'askql')
        level: Log level (defaults to settings.LOG_LEVEL)
    
    Returns:
        Configured logger instance
    """
    if level is None:
        level = settings.LOG_LEVEL
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Optionally add file handler in production
    if settings.is_production():
        try:
            file_handler = logging.FileHandler(
                f'askql_{datetime.now().strftime("%Y%m%d")}.log'
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not set up file logging: {str(e)}")
    
    return logger


def get_logger(name: str = 'askql') -> logging.Logger:
    """
    Get an existing logger or create a new one.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger not configured, set it up
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


# Initialize root logger on module import
root_logger = setup_logger()
