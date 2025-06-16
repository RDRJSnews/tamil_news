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
        logging.FileHandler(f'news_bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
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
12. Generate each word properly, fully and correctly do not use something like �, ��.

Please proceed with generating the news summaries."""

def get_clipboard_content():
    logger.info("Attempting to get clipboard content")
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    try:
        clipboard_content = root.clipboard_get()
        logger.info("Successfully retrieved clipboard content")
    except tk.TclError:
        logger.error("Failed to get clipboard content")
        clipboard_content = ""
    root.destroy()
    return clipboard_content

def run(playwright: Playwright) -> None:
    logger.info("Starting news bot execution")
    try:
        logger.info("Launching browser")
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        logger.info("Navigating to GitHub login page")
        page.goto("https://github.com/login?return_to=https%3A%2F%2Fgithub.com%2Fmarketplace%2Fmodels%2Fazure-openai%2Fgpt-4-1%2Fplayground")
        
        # Get credentials from environment variables
        github_email = os.environ.get('NEWS_BOT_EMAIL')
        github_password = os.environ.get('NEWS_BOT_PASSWORD')
        
        if not github_email or not github_password:
            logger.error("News bot credentials not found in environment variables")
            raise ValueError("News bot credentials not found in environment variables")
        
        logger.info("Attempting to login to GitHub")
        page.get_by_role("textbox", name="Username or email address").fill(github_email)
        page.get_by_role("textbox", name="Password").click()
        page.get_by_role("textbox", name="Password").fill(github_password)
        page.get_by_role("button", name="Sign in", exact=True).click()
        
        logger.info("Navigating to GPT-4 playground")
        page.goto("https://github.com/marketplace/models/azure-openai/gpt-4-1/playground")
        
        logger.info("Setting up GPT-4 parameters")
        page.get_by_role("slider", name="Max Completion Tokens slider").fill("32768")
        page.get_by_role("textbox", name="Prompt", exact=True).click()
        page.get_by_role("textbox", name="Prompt", exact=True).fill(prompt)
        
        logger.info("Sending prompt to GPT-4")
        page.get_by_role("button", name="Send now").click()
        
        logger.info("Copying response to clipboard")
        page.get_by_role("button", name="Copy to clipboard").click()

        # Get clipboard content
        copied_content = get_clipboard_content()
        logger.info("Successfully retrieved news content")
        logger.debug(f"Content length: {len(copied_content)} characters")
        logger.info(f"Content length: {copied_content} characters")

        # ---------------------
        logger.info("Cleaning up browser resources")
        context.close()
        browser.close()
        logger.info("News bot execution completed successfully")

    except Exception as e:
        logger.error(f"An error occurred during execution: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("Starting news bot script")
    try:
        with sync_playwright() as playwright:
            run(playwright)
    except Exception as e:
        logger.error(f"Script failed: {str(e)}", exc_info=True)
        raise
