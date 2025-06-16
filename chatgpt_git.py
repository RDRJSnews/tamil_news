import re
from playwright.sync_api import Playwright, sync_playwright, expect
import tkinter as tk
import os

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
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    try:
        clipboard_content = root.clipboard_get()
    except tk.TclError:
        clipboard_content = ""
    root.destroy()
    return clipboard_content

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)  # Changed to headless=True for GitHub Actions
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://github.com/login?return_to=https%3A%2F%2Fgithub.com%2Fmarketplace%2Fmodels%2Fazure-openai%2Fgpt-4-1%2Fplayground")
    
    # Get credentials from environment variables
    github_email = os.environ.get('NEWS_BOT_EMAIL')
    github_password = os.environ.get('NEWS_BOT_PASSWORD')
    
    if not github_email or not github_password:
        raise ValueError("News bot credentials not found in environment variables")
    
    page.get_by_role("textbox", name="Username or email address").fill(github_email)
    page.get_by_role("textbox", name="Password").click()
    page.get_by_role("textbox", name="Password").fill(github_password)
    page.get_by_role("button", name="Sign in", exact=True).click()
    page.goto("https://github.com/marketplace/models/azure-openai/gpt-4-1/playground")
    
    # Wait for the page to be fully loaded
    page.wait_for_load_state("networkidle")
    
    try:
        # Try to find and fill the max tokens input - using a more reliable selector
        max_tokens_input = page.locator('input[type="range"]').first
        if max_tokens_input:
            max_tokens_input.fill("32768")
        else:
            print("Max tokens input not found, continuing with default value")
    except Exception as e:
        print(f"Warning: Could not set max tokens: {str(e)}")
    
    # Wait for the prompt input to be available
    prompt_input = page.get_by_role("textbox", name="Prompt", exact=True)
    prompt_input.wait_for(state="visible", timeout=10000)
    prompt_input.click()
    prompt_input.fill(prompt)
    
    # Wait for and click the send button
    send_button = page.get_by_role("button", name="Send now")
    send_button.wait_for(state="visible", timeout=10000)
    send_button.click()
    
    # Wait for response and copy button
    copy_button = page.get_by_role("button", name="Copy to clipboard")
    copy_button.wait_for(state="visible", timeout=30000)  # Increased timeout for response
    copy_button.click()

    # Get clipboard content
    copied_content = get_clipboard_content()
    print("Copied content:", copied_content)

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
