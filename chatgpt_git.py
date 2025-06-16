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
12. Generate each word properly, fully and correctly do not use something like �, ��, ..etc.

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
    browser = playwright.chromium.launch(headless=False)  # Changed to headless=True for GitHub Actions
    context = browser.new_context()
    page = context.new_page()
    
    logger.info("Navigating to GitHub login")
    page.goto("https://github.com/login?return_to=https%3A%2F%2Fgithub.com%2Fmarketplace%2Fmodels%2Fazure-openai%2Fgpt-4-1%2Fplayground")
    
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
    page.goto("https://github.com/marketplace/models/azure-openai/gpt-4-1/playground")
    
    logger.info("Setting up GPT-4 parameters")
    try:
        # Wait for the spinbutton to be visible and ready
        spinbutton = page.get_by_role("spinbutton", name="Max Completion Tokens")
        spinbutton.wait_for(state="visible", timeout=60000)  # Increased timeout to 60 seconds
        
        # Click and fill the spinbutton
        spinbutton.click(timeout=30000)
        spinbutton.press("ControlOrMeta+a")
        spinbutton.fill("32768")
        
        # Wait for and fill the prompt textbox
        prompt_textbox = page.get_by_role("textbox", name="Prompt", exact=True)
        prompt_textbox.wait_for(state="visible", timeout=30000)
        prompt_textbox.click()
        prompt_textbox.fill(prompt)
        
        logger.info("Sending prompt to GPT-4")
        page.get_by_role("button", name="Send now").click()
        
        logger.info("Waiting for response and copying")
        copy_button = page.get_by_role("button", name="Copy to clipboard")
        copy_button.wait_for(state="visible", timeout=30000)
        copy_button.click()
    except Exception as e:
        logger.error(f"Failed to set up GPT-4 parameters: {str(e)}")
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
