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
0. DO NOT REPEAT any news from previous requests. Generate entirely new content.
1. First line must be: "Today's National News:"
2. Format each news as: "Title: Summary."
3. Use ₹14588 instead of ₹14,588 (no commas in numbers).
4. Plain text only (no **, ##, etc.).
5. Include 15 unique news items.
6. Start immediately without explanations.
7. End each line with punctuation (. or , or :).
8. Source format: ". News Provided By: dinamalar." (no URLs/emojis).
9. Last line: "For more Daily News, do like, share, subscribe and comment."
10. No extra text before/after the news.
11. Prioritize DIFFERENT topics than previous runs.
12. Focus on FRESH events (avoid older than 24 hours).

Generate now:"""

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
0. முன்பு வெளியிட்ட செய்திகளை திரும்ப செய்யாதீர்கள். புதிய தகவல்களை மட்டுமே தரவும்.
1. முதல் வரி: "இன்றைய தேசிய செய்திகள்:"
2. வடிவம்: "தலைப்பு: சுருக்கம்."
3. ₹14588 போன்று எண்களில் கமாவை தவிர்க்கவும்.
4. எளிய உரை (**, ## இல்லை).
5. 15 தனித்துவமான செய்திகள்.
6. உடனடியாக தொடங்கவும்.
7. ஒவ்வொரு வரியையும் . , அல்லது : உடன் முடிக்கவும்.
8. மூலம்: ". செய்திகள் வலங்கியது: விகடன்."
9. கடைசி வரி: "இது போல தினசரி செய்திகள் தெரிந்துகொள்ள like, share, subscribe மற்றும் comment செய்யுங்கள்."
10. மேலதிக உரையை சேர்க்காதீர்கள்.
11. முந்தைய கோரிக்கைகளில் இல்லாத தலைப்புகளை தேர்வு செய்யவும்.
12. புதிய நிகழ்வுகளில் கவனம் செலுத்தவும் (24 மணி நேரத்திற்கு முன்பு இல்லாதவை).

உடனடியாக உருவாக்கவும்:"""

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
0. पिछली खबरों को दोहराएं नहीं। नई सामग्री उत्पन्न करें।
1. पहली पंक्ति: "आज की राष्ट्रीय खबरें:"
2. प्रारूप: "शीर्षक: सारांश."
3. ₹14588 का उपयोग करें (अल्पविराम नहीं)।
4. सादा पाठ (**, ## नहीं)।
5. 15 अद्वितीय समाचार।
6. बिना स्पष्टीकरण के शुरू करें।
7. प्रत्येक पंक्ति को . , या : से समाप्त करें।
8. स्रोत: ". इस समाचार की पुष्टि निम्नलिखित द्वारा की गई है: ndtv."
9. अंतिम पंक्ति: "ऐसे ही दैनिक समाचार जानने के लिए like, share, subscribe और comment इसे करें।"
10. अतिरिक्त पाठ न जोड़ें।
11. पिछले अनुरोधों से अलग विषय चुनें।
12. नई घटनाओं पर ध्यान दें (24 घंटे से अधिक पुरानी नहीं)।

अभी उत्पन्न करें:"""

# Configure API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY environment variable not set!")
genai.configure(api_key=GEMINI_API_KEY)

def setup_model():
    """Configure model with randomized parameters for diversity."""
    generation_config = {
        "temperature": random.uniform(0.8, 1.0),  # High randomness
        "top_p": random.uniform(0.8, 0.95),
        "top_k": random.randint(30, 50),
        "max_output_tokens": 2048,
    }
    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
    return genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=generation_config,
        safety_settings=safety_settings
    )

def format_response(text):
    """Format news text for readability."""
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        if not line.strip():
            continue
        if ':' in line and not line.strip().endswith(':'):
            title, content = line.split(':', 1)
            formatted_lines.append(f"{title.strip()}:")
            formatted_lines.append(textwrap.fill(content.strip(), width=75, initial_indent='  ', subsequent_indent='  '))
        else:
            formatted_lines.append(line)
    return '\n'.join(formatted_lines)

def get_gemini_response(prompt):
    """Fetch response from Gemini API."""
    model = setup_model()
    try:
        response = model.generate_content(prompt)
        return format_response(response.text)
    except Exception as e:
        return f"Error: {str(e)}"

def main(lang='en-in'):
    log_print("INFO", f"Generating news in {lang}...")
    prompt = {
        'en-in': get_prompt_en(),
        'ta': get_prompt_ta(),
        'hi': get_prompt_hi()
    }.get(lang, get_prompt_en())
    return get_gemini_response(prompt)

if __name__ == "__main__":
    print(main('en-in'))  # Test with English
