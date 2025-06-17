#!/usr/bin/env python3
"""
Main workflow script for Tamil News Generation and Upload
This script orchestrates the entire process from news generation to YouTube upload
"""

import sys
import time
from datetime import datetime
from logger_config import get_logger

# Import all the modules
from news_text import main as news_text_main
from news_audio import main as news_audio_main
from news_video import main as news_video_main
from upload_youtube import authenticate_youtube, upload_video, TITLE, DESCRIPTION, TAGS

# Set up logger for main workflow
logger = get_logger(__name__)

def run_news_text_generation(lang='en-in'):
    """Run news text generation process."""
    logger.info("=" * 60)
    logger.info("STEP 1: NEWS TEXT GENERATION")
    logger.info("=" * 60)
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting news text generation for language: {lang}")
        news_text = news_text_main(lang)
        
        if not news_text or news_text.startswith("An error occurred"):
            raise Exception("News text generation failed")
        
        elapsed_time = time.time() - start_time
        logger.info(f"News text generation completed successfully in {elapsed_time:.2f} seconds")
        logger.debug(f"Generated text length: {len(news_text)} characters")
        
        return news_text
        
    except Exception as e:
        logger.error(f"News text generation failed: {str(e)}")
        raise

def run_audio_generation(lang_code=1):
    """Run audio generation process."""
    logger.info("=" * 60)
    logger.info("STEP 2: AUDIO GENERATION")
    logger.info("=" * 60)
    
    start_time = time.time()
    
    try:
        logger.info(f"Starting audio generation for language code: {lang_code}")
        audio_buffer = news_audio_main(lang_code)
        
        if not audio_buffer:
            raise Exception("Audio generation failed")
        
        elapsed_time = time.time() - start_time
        logger.info(f"Audio generation completed successfully in {elapsed_time:.2f} seconds")
        logger.debug(f"Audio buffer size: {len(audio_buffer.getvalue())} bytes")
        
        return audio_buffer
        
    except Exception as e:
        logger.error(f"Audio generation failed: {str(e)}")
        raise

def run_video_generation():
    """Run video generation process."""
    logger.info("=" * 60)
    logger.info("STEP 3: VIDEO GENERATION")
    logger.info("=" * 60)
    
    start_time = time.time()
    
    try:
        logger.info("Starting video generation process")
        video_buffer = news_video_main()
        
        if not video_buffer:
            raise Exception("Video generation failed")
        
        elapsed_time = time.time() - start_time
        logger.info(f"Video generation completed successfully in {elapsed_time:.2f} seconds")
        logger.debug(f"Video buffer size: {len(video_buffer.getvalue())} bytes")
        
        return video_buffer
        
    except Exception as e:
        logger.error(f"Video generation failed: {str(e)}")
        raise

def run_youtube_upload(video_buffer):
    """Run YouTube upload process."""
    logger.info("=" * 60)
    logger.info("STEP 4: YOUTUBE UPLOAD")
    logger.info("=" * 60)
    
    start_time = time.time()
    
    try:
        logger.info("Starting YouTube upload process")
        logger.info(f"Video title: {TITLE}")
        logger.info(f"Description length: {len(DESCRIPTION)} characters")
        logger.info(f"Tags: {TAGS}")
        
        # Authenticate with YouTube
        logger.info("Authenticating with YouTube API")
        youtube = authenticate_youtube()
        
        # Upload video
        logger.info("Uploading video to YouTube")
        upload_video(youtube, TITLE, video_buffer)
        
        elapsed_time = time.time() - start_time
        logger.info(f"YouTube upload completed successfully in {elapsed_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        logger.error(f"YouTube upload failed: {str(e)}")
        raise

def main():
    """Main workflow function."""
    logger.info("=" * 80)
    logger.info("TAMIL NEWS GENERATION AND UPLOAD WORKFLOW")
    logger.info("=" * 80)
    logger.info(f"Workflow started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    overall_start_time = time.time()
    
    try:
        # Step 1: Generate news text
        news_text = run_news_text_generation('en-in')
        
        # Step 2: Generate audio
        audio_buffer = run_audio_generation(1)
        
        # Step 3: Generate video
        video_buffer = run_video_generation()
        
        # Step 4: Upload to YouTube
        upload_success = run_youtube_upload(video_buffer)
        
        overall_elapsed_time = time.time() - overall_start_time
        logger.info("=" * 80)
        logger.info("WORKFLOW COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"Total workflow time: {overall_elapsed_time:.2f} seconds")
        logger.info(f"Workflow completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        overall_elapsed_time = time.time() - overall_start_time
        logger.error("=" * 80)
        logger.error("WORKFLOW FAILED!")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}")
        logger.error(f"Workflow failed after {overall_elapsed_time:.2f} seconds")
        logger.error(f"Failure time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return False

def run_with_retry(max_retries=3):
    """Run the workflow with retry logic."""
    logger.info(f"Starting workflow with max retries: {max_retries}")
    
    for attempt in range(1, max_retries + 1):
        logger.info(f"Attempt {attempt}/{max_retries}")
        
        try:
            success = main()
            if success:
                logger.info("Workflow completed successfully!")
                return True
            else:
                logger.warning(f"Workflow failed on attempt {attempt}")
                
        except Exception as e:
            logger.error(f"Workflow failed on attempt {attempt}: {str(e)}")
        
        if attempt < max_retries:
            logger.info(f"Waiting 30 seconds before retry...")
            time.sleep(30)
    
    logger.error(f"Workflow failed after {max_retries} attempts")
    return False

if __name__ == "__main__":
    try:
        # Check if retry mode is requested
        if len(sys.argv) > 1 and sys.argv[1] == "--retry":
            success = run_with_retry()
        else:
            success = main()
        
        if success:
            logger.info("Exiting with success code 0")
            sys.exit(0)
        else:
            logger.error("Exiting with error code 1")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in main: {str(e)}")
        sys.exit(1) 