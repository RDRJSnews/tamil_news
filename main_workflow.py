#!/usr/bin/env python3
"""
Main workflow script for Tamil News Generation and Upload
This script orchestrates the entire process from news generation to YouTube upload
"""

import sys
import time
from datetime import datetime

# Import all the modules
from news_text import main as news_text_main
from news_audio import main as news_audio_main
from news_video import main as news_video_main
from upload_youtube import authenticate_youtube, upload_video, TITLE, DESCRIPTION, TAGS

def log_print(level, message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}")

def run_news_text_generation(lang='en-in'):
    """Run news text generation process."""
    log_print("INFO", "=" * 60)
    log_print("INFO", "STEP 1: NEWS TEXT GENERATION")
    log_print("INFO", "=" * 60)
    
    start_time = time.time()
    
    try:
        log_print("INFO", f"Starting news text generation for language: {lang}")
        news_text = news_text_main(lang)
        
        if not news_text or news_text.startswith("An error occurred"):
            raise Exception("News text generation failed")
        
        elapsed_time = time.time() - start_time
        log_print("INFO", f"News text generation completed successfully in {elapsed_time:.2f} seconds")
        log_print("DEBUG", f"Generated text length: {len(news_text)} characters")
        
        return news_text
        
    except Exception as e:
        log_print("ERROR", f"News text generation failed: {str(e)}")
        raise

def run_audio_generation(lang_code=1):
    """Run audio generation process."""
    log_print("INFO", "=" * 60)
    log_print("INFO", "STEP 2: AUDIO GENERATION")
    log_print("INFO", "=" * 60)
    
    start_time = time.time()
    
    try:
        log_print("INFO", f"Starting audio generation for language code: {lang_code}")
        audio_buffer = news_audio_main(lang_code)
        
        if not audio_buffer:
            raise Exception("Audio generation failed")
        
        elapsed_time = time.time() - start_time
        log_print("INFO", f"Audio generation completed successfully in {elapsed_time:.2f} seconds")
        log_print("DEBUG", f"Audio buffer size: {len(audio_buffer.getvalue())} bytes")
        
        return audio_buffer
        
    except Exception as e:
        log_print("ERROR", f"Audio generation failed: {str(e)}")
        raise

def run_video_generation():
    """Run video generation process."""
    log_print("INFO", "=" * 60)
    log_print("INFO", "STEP 3: VIDEO GENERATION")
    log_print("INFO", "=" * 60)
    
    start_time = time.time()
    
    try:
        log_print("INFO", "Starting video generation process")
        video_buffer = news_video_main()
        
        if not video_buffer:
            raise Exception("Video generation failed")
        
        elapsed_time = time.time() - start_time
        log_print("INFO", f"Video generation completed successfully in {elapsed_time:.2f} seconds")
        log_print("DEBUG", f"Video buffer size: {len(video_buffer.getvalue())} bytes")
        
        return video_buffer
        
    except Exception as e:
        log_print("ERROR", f"Video generation failed: {str(e)}")
        raise

def run_youtube_upload(video_buffer):
    """Run YouTube upload process."""
    log_print("INFO", "=" * 60)
    log_print("INFO", "STEP 4: YOUTUBE UPLOAD")
    log_print("INFO", "=" * 60)
    
    start_time = time.time()
    
    try:
        log_print("INFO", "Starting YouTube upload process")
        log_print("INFO", f"Video title: {TITLE}")
        log_print("INFO", f"Description length: {len(DESCRIPTION)} characters")
        log_print("INFO", f"Tags: {TAGS}")
        
        # Authenticate with YouTube
        log_print("INFO", "Authenticating with YouTube API")
        youtube = authenticate_youtube()
        
        # Upload video
        log_print("INFO", "Uploading video to YouTube")
        upload_video(youtube, TITLE, video_buffer)
        
        elapsed_time = time.time() - start_time
        log_print("INFO", f"YouTube upload completed successfully in {elapsed_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        log_print("ERROR", f"YouTube upload failed: {str(e)}")
        raise

def main():
    """Main workflow function."""
    log_print("INFO", "=" * 80)
    log_print("INFO", "TAMIL NEWS GENERATION AND UPLOAD WORKFLOW")
    log_print("INFO", "=" * 80)
    log_print("INFO", f"Workflow started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
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
        log_print("INFO", "=" * 80)
        log_print("INFO", "WORKFLOW COMPLETED SUCCESSFULLY!")
        log_print("INFO", "=" * 80)
        log_print("INFO", f"Total workflow time: {overall_elapsed_time:.2f} seconds")
        log_print("INFO", f"Workflow completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        overall_elapsed_time = time.time() - overall_start_time
        log_print("ERROR", "=" * 80)
        log_print("ERROR", "WORKFLOW FAILED!")
        log_print("ERROR", "=" * 80)
        log_print("ERROR", f"Error: {str(e)}")
        log_print("ERROR", f"Workflow failed after {overall_elapsed_time:.2f} seconds")
        log_print("ERROR", f"Failure time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return False

def run_with_retry(max_retries=3):
    """Run the workflow with retry logic."""
    log_print(f"INFO", f"Starting workflow with max retries: {max_retries}")
    
    for attempt in range(1, max_retries + 1):
        log_print(f"INFO", f"Attempt {attempt}/{max_retries}")
        
        try:
            success = main()
            if success:
                log_print("INFO", "Workflow completed successfully!")
                return True
            else:
                log_print("WARNING", f"Workflow failed on attempt {attempt}")
                
        except Exception as e:
            log_print("ERROR", f"Workflow failed on attempt {attempt}: {str(e)}")
        
        if attempt < max_retries:
            log_print(f"INFO", f"Waiting 30 seconds before retry...")
            time.sleep(30)
    
    log_print("ERROR", f"Workflow failed after {max_retries} attempts")
    return False

if __name__ == "__main__":
    try:
        # Check if retry mode is requested
        if len(sys.argv) > 1 and sys.argv[1] == "--retry":
            success = run_with_retry()
        else:
            success = main()
        
        if success:
            log_print("INFO", "Exiting with success code 0")
            sys.exit(0)
        else:
            log_print("ERROR", "Exiting with error code 1")
            sys.exit(1)
            
    except KeyboardInterrupt:
        log_print("WARNING", "Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        log_print("ERROR", f"Unexpected error in main: {str(e)}")
        sys.exit(1) 