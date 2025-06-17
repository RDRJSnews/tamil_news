#!/usr/bin/env python3
"""
Test script to verify logging functionality across all modules
"""

import sys
import os
from logger_config import get_logger

# Set up logger for this test
logger = get_logger(__name__)

def test_logger_config():
    """Test the logger configuration."""
    logger.info("=== Testing Logger Configuration ===")
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Check if logs directory was created
    if os.path.exists("logs"):
        logger.info("Logs directory created successfully")
        log_files = os.listdir("logs")
        logger.info(f"Log files found: {log_files}")
    else:
        logger.error("Logs directory not found")
    
    logger.info("Logger configuration test completed")

def test_news_text_module():
    """Test the news_text module logging."""
    logger.info("=== Testing News Text Module ===")
    
    try:
        from news_text import main as news_text_main
        
        # Test with English
        logger.info("Testing English news generation")
        result = news_text_main('en-in')
        if result and not result.startswith("An error occurred"):
            logger.info("English news generation test passed")
        else:
            logger.error("English news generation test failed")
        
        # Test with Tamil
        logger.info("Testing Tamil news generation")
        result = news_text_main('ta')
        if result and not result.startswith("An error occurred"):
            logger.info("Tamil news generation test passed")
        else:
            logger.error("Tamil news generation test failed")
            
    except Exception as e:
        logger.error(f"News text module test failed: {str(e)}")

def test_news_audio_module():
    """Test the news_audio module logging."""
    logger.info("=== Testing News Audio Module ===")
    
    try:
        from news_audio import main as news_audio_main
        
        # Test audio generation
        logger.info("Testing audio generation")
        result = news_audio_main(1)  # English
        if result:
            logger.info("Audio generation test passed")
        else:
            logger.error("Audio generation test failed")
            
    except Exception as e:
        logger.error(f"News audio module test failed: {str(e)}")

def test_news_video_module():
    """Test the news_video module logging."""
    logger.info("=== Testing News Video Module ===")
    
    try:
        from news_video import main as news_video_main
        
        # Test video generation
        logger.info("Testing video generation")
        result = news_video_main()
        if result:
            logger.info("Video generation test passed")
        else:
            logger.error("Video generation test failed")
            
    except Exception as e:
        logger.error(f"News video module test failed: {str(e)}")

def test_youtube_upload_module():
    """Test the YouTube upload module logging."""
    logger.info("=== Testing YouTube Upload Module ===")
    
    try:
        from upload_youtube import authenticate_youtube
        
        # Test authentication (without actually uploading)
        logger.info("Testing YouTube authentication")
        youtube = authenticate_youtube()
        if youtube:
            logger.info("YouTube authentication test passed")
        else:
            logger.error("YouTube authentication test failed")
            
    except Exception as e:
        logger.error(f"YouTube upload module test failed: {str(e)}")

def main():
    """Run all logging tests."""
    logger.info("=" * 60)
    logger.info("STARTING LOGGING SYSTEM TESTS")
    logger.info("=" * 60)
    
    try:
        # Test logger configuration
        test_logger_config()
        
        # Test individual modules
        test_news_text_module()
        test_news_audio_module()
        test_news_video_module()
        test_youtube_upload_module()
        
        logger.info("=" * 60)
        logger.info("ALL LOGGING TESTS COMPLETED")
        logger.info("=" * 60)
        logger.info("Check the logs directory for detailed log files")
        
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 