import google.generativeai as genai
import textwrap
import os
from datetime import datetime
import time
import random

def log_print(level, message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}")

def get_prompt_en():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_date = datetime.now().strftime('%Y-%m-%d')
    random_seed = random.randint(1, 10000)
    time_variations = [
        f"latest breaking news as of {current_time}",
        f"current national headlines for {current_date}",
        f"today's top stories updated at {current_time}",
        f"breaking national news for {current_date}",
        f"latest developments as of {current_time}"
    ]
    selected_variation = random.choice(time_variations)
    
    return f"""TL;DR: Generate {selected_variation} in English language (request #{random_seed}).

Requirements and rules:
0. Do not use any catch news that you havee already generated in the previous request, do not repeat the same news, do not use the same news in the same request, delete and forget the previous news, and completely generate new news.
1. Always the first line with be "Today's National News:"
2. Generate each news with a suitable title then : followed by the respective news summay
3. Do not use commas in numbers (e.g., use ₹14588 instead of ₹14,588)
4. Generate in plain text without any special characters (**, ##, etc.)
5. Collect maximum possible news
6. Start generating news immediately without explanations
7. Must end each line with appropriate punctuation (. or , or :)
8. Do not include emojis or URLs—mention only the domain name (e.g., dinamalar, vikatan, thehindu, ndtv, etc.) after the word ". News Provided By:" at the end of the news summary and ending with '.'.
9. Always the last line will be 'For more Daily News, do like, share, subscribe and comment .'
10. Do not use any other text or comments before or after the news summaries.
11. Generate 15 most important and priority news.
12. Focus on DIFFERENT news stories than previous requests - avoid repetition.

Please proceed with generating the news summaries."""

def get_prompt_ta():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_date = datetime.now().strftime('%Y-%m-%d')
    random_seed = random.randint(1, 10000)
    time_variations = [
        f"சமீபத்திய செய்திகள் {current_time} நேரத்தில்",
        f"தற்போதைய தேசிய செய்திகள் {current_date} க்கான",
        f"இன்றைய முக்கிய செய்திகள் {current_time} புதுப்பிக்கப்பட்டது",
        f"சமீபத்திய முன்னேற்றங்கள் {current_time} நேரத்தில்",
        f"தற்போதைய முக்கிய செய்திகள் {current_date} க்கான"
    ]
    selected_variation = random.choice(time_variations)
    
    return f"""TL;DR: Generate {selected_variation} in Tamil language (request #{random_seed}).

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
11. Generate 15 most important and priority news.
12. Focus on DIFFERENT news stories than previous requests - avoid repetition.

Please proceed with generating the news summaries."""

def get_prompt_hi():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    current_date = datetime.now().strftime('%Y-%m-%d')
    random_seed = random.randint(1, 10000)
    time_variations = [
        f"latest breaking news as of {current_time}",
        f"current national headlines for {current_date}",
        f"today's top stories updated at {current_time}",
        f"breaking national news for {current_date}",
        f"latest developments as of {current_time}"
    ]
    selected_variation = random.choice(time_variations)
    
    return f"""TL;DR: Generate {selected_variation} in Hindi language (request #{random_seed}).

Requirements and rules:
1. Always the first line with be 'आज की राष्ट्रीय खबरें:'
2. Generate each news with a suitable title then : followed by the respective news summay
3. Do not use commas in numbers (e.g., use ₹14588 instead of ₹14,588)
4. Generate in plain text without any special characters (**, ##, etc.)
5. Collect maximum possible news
6. Start generating news immediately without explanations
7. Must end each line with appropriate punctuation (. or , or :)
8. Do not include emojis or URLs—mention only the domain name (e.g., dinamalar, vikatan, thehindu, ndtv, etc.) after the word ". इस समाचार की पुष्टि निम्नलिखित द्वारा की गई है:" at the end of the news summary and ending with '.'.
9. Always the last line will be 'ऐसे ही दैनिक समाचार जानने के लिए like, share, subscribe और comment इसे करें.'
10. Do not use any other text or comments before or after the news summaries.
11. Generate 15 most important and priority news.
12. Focus on DIFFERENT news stories than previous requests - avoid repetition.

Please proceed with generating the news summaries."""

# Configure the API with your key from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set!")

log_print("INFO", "Configuring Gemini API with environment variable")
genai.configure(api_key=GEMINI_API_KEY)

def list_available_models():
    """List all available models."""
    log_print("INFO", "Listing available Gemini models")
    try:
        for m in genai.list_models():
            log_print("DEBUG", f"Model: {m.name}")
            log_print("DEBUG", f"Display name: {m.display_name}")
            log_print("DEBUG", f"Description: {m.description}")
            log_print("---")
        log_print("INFO", "Successfully listed available models")
    except Exception as e:
        log_print("ERROR", f"Error listing models: {str(e)}")
        raise

def setup_model():
    """Set up the Gemini model with optimized parameters."""
    log_print("INFO", "Setting up Gemini model with optimized parameters")
    
    # Add more randomness to ensure different responses
    temperature = random.uniform(0.8, 1.0)  # Random temperature between 0.8-1.0
    top_p = random.uniform(0.8, 0.95)      # Random top_p between 0.8-0.95
    top_k = random.randint(30, 50)         # Random top_k between 30-50
    
    generation_config = {
        "temperature": temperature,  # Increased randomness (0.0 to 1.0)
        "top_p": top_p,            # Nucleus sampling parameter
        "top_k": top_k,            # Top-k sampling parameter
        "max_output_tokens": 2048,  # Maximum length of response
    }
    
    log_print("INFO", f"Using temperature: {temperature:.2f}, top_p: {top_p:.2f}, top_k: {top_k}")
    
    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]
    
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    
    log_print("INFO", "Gemini model setup completed successfully")
    return model

def format_response(text):
    """Format the response text for better readability."""
    log_print("DEBUG", "Starting text formatting process")
    log_print("DEBUG", f"Original text length: {len(text)} characters")
    
    # Split the text into lines
    lines = text.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            continue
            
        # Handle the title lines (both Tamil and English)
        if line.startswith('இன்றைய தேசிய செய்திகள்:') or line.startswith("Today's National News:"):
            formatted_lines.append(line)
            log_print("DEBUG", f"Added title line: {line[:50]}...")
            continue
            
        # Handle the source lines (both Tamil and English)
        if 'செய்திகள் வலங்கியது:' in line or 'News Provided By:' in line:
            formatted_lines.append(line)
            log_print("DEBUG", f"Added source line: {line[:50]}...")
            continue
            
        # Handle the social media lines (both Tamil and English)
        if ('இது போல தினசரி செய்திகள்' in line or 
            'For more Daily News' in line):
            formatted_lines.append(line)
            log_print("DEBUG", f"Added social media line: {line[:50]}...")
            continue
            
        # Format regular news lines
        if ':' in line and not line.strip().endswith(':'):
            # Split only on the first colon to preserve any colons in the content
            parts = line.split(':', 1)
            if len(parts) == 2:
                title, content = parts
                formatted_lines.append(f"{title.strip()}:")
                # Wrap the content with proper indentation
                wrapped_content = textwrap.fill(content.strip(), width=75, initial_indent='  ', subsequent_indent='  ')
                formatted_lines.append(wrapped_content)
                log_print("DEBUG", f"Formatted news line {i+1}: {title.strip()[:30]}...")
            else:
                formatted_lines.append(line)
                log_print("DEBUG", f"Added unformatted line {i+1}: {line[:50]}...")
        else:
            formatted_lines.append(line)
            log_print("DEBUG", f"Added simple line {i+1}: {line[:50]}...")
    
    formatted_text = '\n'.join(formatted_lines)
    log_print("INFO", f"Text formatting completed. Final length: {len(formatted_text)} characters")
    return formatted_text

def get_gemini_response(prompt):
    """Get response from Gemini API for the given prompt."""
    log_print("INFO", "Initiating Gemini API request")
    log_print("DEBUG", f"Prompt length: {len(prompt)} characters")
    
    model = setup_model()
    
    try:
        log_print("INFO", "Sending request to Gemini API...")
        response = model.generate_content(prompt)
        log_print("INFO", "Received response from Gemini API")
        log_print("DEBUG", f"Raw response length: {len(response.text)} characters")
        
        formatted_response = format_response(response.text)
        log_print("INFO", "Successfully processed Gemini response")
        return formatted_response
    except Exception as e:
        log_print("ERROR", f"Error getting Gemini response: {str(e)}")
        return f"An error occurred: {str(e)}"

def main(lang):
    log_print("INFO", "=== Starting News Text Generation Process ===")
    log_print("INFO", f"Selected language: {lang}")
    
    if lang == 'en-in':
        prompt = get_prompt_en()
        log_print("INFO", "Using English prompt")
    elif lang == 'ta':
        prompt = get_prompt_ta()
        log_print("INFO", "Using Tamil prompt")
    elif lang == 'hi':
        prompt = get_prompt_hi()
        log_print("INFO", "Using Hindi prompt")
    else:
        log_print("ERROR", f"Unsupported language: {lang}")
        raise ValueError(f"Unsupported language: {lang}")
    
    log_print("INFO", "Generating news content with Gemini AI...")
    response = get_gemini_response(prompt)
    
    if response.startswith("An error occurred"):
        log_print("ERROR", "Failed to generate news content")
        return response
    
    log_print("INFO", "=== News Text Generation Completed Successfully ===")
    return response

# if __name__ == "__main__":
#     main(ta)
