import logging
import os
from datetime import datetime
import sys

def setup_logger(name, log_level=logging.INFO):
    """
    Set up a logger with file and console handlers.
    
    Args:
        name (str): Name of the logger (usually __name__)
        log_level: Logging level (default: INFO)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create file handler for detailed logs
    today = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.FileHandler(
        os.path.join(logs_dir, f'tamil_news_{today}.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Create console handler for important logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Create error file handler
    error_handler = logging.FileHandler(
        os.path.join(logs_dir, f'errors_{today}.log'),
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(error_handler)
    
    return logger

def get_logger(name):
    """
    Get a logger instance for the given name.
    
    Args:
        name (str): Name of the logger (usually __name__)
    
    Returns:
        logging.Logger: Logger instance
    """
    return setup_logger(name) 