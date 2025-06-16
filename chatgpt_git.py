import re
from playwright.sync_api import Playwright, sync_playwright, expect
import tkinter as tk
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only log to console for GitHub Actions
    ]
)
logger = logging.getLogger(__name__)

prompt = """Generate today's National news summaries in Tamil language.

Requirements and rules:
1. Always the first line with be 'இன்றைய தேசிய செய்திகள்:'
2. Generate each news with a suitable title then : followed by the respective news summay
3. Do not use commas in numbers (e.g., use ₹14588 instead of ₹14,588)
4. Generate in plain text without any special characters (**, ##, etc.)
5. Collect maximum possible news
6. Start generating news immediately without explanations
7. Must end each line with appropriate punctuation (. or , or :)
8. Do not include emojis or URLs—mention only the domain name (e.g., dinamalar, vikatan, thehindu, ndtv, etc.) after the word ". செய்திகள் வலங்கியது:" at the end of the news summary and ending with '.'.
9. Always the last line will be 'இது போல தினசரி செய்திகள் தெரிந்துகொள்ள like, share, subscribe மற்றும் comment செய்யுங்கள்.'
10. Do not use any other text or comments before or after the news summaries.
11. Generate more than 20+ important and priority news.
12. Generate each word properly, fully and correctly do not use something like �, ��, ..etc(exclude all patterns like this).

Please proceed with generating the news summaries."""

def get_clipboard_content():
    logger.info("Getting clipboard content")
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    try:
        clipboard_content = root.clipboard_get()
        logger.info("Successfully got clipboard content")
    except tk.TclError:
        logger.error("Failed to get clipboard content")
        clipboard_content = ""
    root.destroy()
    return clipboard_content

def run(playwright: Playwright) -> None:
    logger.info("Starting news bot")
    browser = playwright.chromium.launch(
        headless=True,  # Force headless mode for GitHub Actions
        args=['--disable-dev-shm-usage', '--no-sandbox']  # Additional args for stability
    )
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},  # Set a specific viewport
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'  # Set a specific user agent
    )
    page = context.new_page()
    
    logger.info("Navigating to GitHub login")
    page.goto("https://github.com/login?return_to=https%3A%2F%2Fgithub.com%2Fmarketplace%2Fmodels%2Fazure-openai%2Fgpt-4-1%2Fplayground", wait_until="networkidle")
    
    # Get credentials from environment variables
    github_email = os.environ.get('NEWS_BOT_EMAIL')
    github_password = os.environ.get('NEWS_BOT_PASSWORD')
    
    if not github_email or not github_password:
        logger.error("GitHub credentials not found")
        raise ValueError("GitHub credentials not found in environment variables")
    
    logger.info("Logging into GitHub")
    page.get_by_role("textbox", name="Username or email address").fill(github_email)
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(github_password)
    page.get_by_role("button", name="Sign in", exact=True).click()
    
    logger.info("Navigating to GPT-4 playground")
    page.goto("https://github.com/marketplace/models/azure-openai/gpt-4-1/playground", wait_until="networkidle")
    
    logger.info("Setting up GPT-4 parameters")
    try:
        # Wait for the page to be fully loaded
        page.wait_for_load_state("networkidle")
        
        # Try multiple strategies to find and interact with the spinbutton
        spinbutton = None
        for attempt in range(3):  # Try up to 3 times
            try:
                spinbutton = page.get_by_role("spinbutton", name="Max Completion Tokens")
                if spinbutton.is_visible():
                    break
                page.wait_for_timeout(5000)  # Wait 5 seconds between attempts
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} to find spinbutton failed: {str(e)}")
                if attempt == 2:  # Last attempt
                    raise
                page.reload()
                page.wait_for_load_state("networkidle")
        
        if spinbutton:
            spinbutton.click()
            spinbutton.press("ControlOrMeta+a")
            spinbutton.fill("32768")
        
        # Wait for and fill the prompt textbox
        prompt_textbox = page.get_by_role("textbox", name="Prompt", exact=True)
        prompt_textbox.wait_for(state="attached", timeout=30000)  # Use 'attached' instead of 'visible'
        prompt_textbox.click()
        prompt_textbox.fill(prompt)
        
        logger.info("Sending prompt to GPT-4")
        page.get_by_role("button", name="Send now").click()
        
        logger.info("Waiting for response and copying")
        copy_button = page.get_by_role("button", name="Copy to clipboard")
        copy_button.wait_for(state="attached", timeout=30000)  # Use 'attached' instead of 'visible'
        copy_button.click()
    except Exception as e:
        logger.error(f"Failed to set up GPT-4 parameters: {str(e)}")
        # Take a screenshot for debugging
        page.screenshot(path="error-screenshot.png")
        raise

    # Get clipboard content
    copied_content = get_clipboard_content()
    logger.info(f"Retrieved content length: {len(copied_content)} characters")
    logger.info(f"Retrieved content length: {copied_content} characters")
    print("Copied content:", copied_content)

    # ---------------------
    logger.info("Cleaning up browser")
    context.close()
    browser.close()
    logger.info("News bot completed")

with sync_playwright() as playwright:
    try:
        run(playwright)
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        raise
