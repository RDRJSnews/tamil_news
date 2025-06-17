from news_text import main as news_text_main
from gtts import gTTS
import io
from logger_config import get_logger

# Set up logger for this module
logger = get_logger(__name__)

def tamil_news_reader(text, lang):
    """Generate speech from text using gTTS."""
    logger.info("=== Starting Text-to-Speech Conversion ===")
    logger.info(f"Language: {lang}")
    logger.info(f"Text length: {len(text)} characters")
    
    try:
        logger.info("Initializing gTTS with specified parameters")
        # Generate Tamil speech
        tts = gTTS(text=text, lang=lang, slow=False)
        logger.info("gTTS object created successfully")
        
        # Save to bytes buffer instead of file
        logger.info("Converting speech to audio buffer")
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        buffer_size = len(audio_buffer.getvalue())
        logger.info(f"Audio buffer created successfully. Size: {buffer_size} bytes")
        logger.info("=== Text-to-Speech Conversion Completed Successfully ===")
        
        return audio_buffer
        
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {str(e)}")
        raise

def main(lang_code):
    """Main function to generate news audio."""
    logger.info("=== Starting News Audio Generation Process ===")
    logger.info(f"Language code received: {lang_code}")
    
    # Tamil English news text
    langs = ['ta', 'en-in']
    
    if lang_code < 0 or lang_code >= len(langs):
        logger.error(f"Invalid language code: {lang_code}. Valid range: 0-{len(langs)-1}")
        raise ValueError(f"Invalid language code: {lang_code}")
    
    lang = langs[lang_code]
    logger.info(f"Selected language: {lang} (code: {lang_code})")
    
    try:
        logger.info("Calling news_text_main to generate news content")
        news_text = news_text_main(lang)
        
        if not news_text or news_text.startswith("An error occurred"):
            logger.error("Failed to get news text from news_text_main")
            raise Exception("News text generation failed")
        
        logger.info("News text generated successfully")
        logger.debug(f"News text preview: {news_text[:100]}...")
        
        # Generate audio from text
        audio_buffer = tamil_news_reader(news_text, lang)
        
        logger.info("=== News Audio Generation Completed Successfully ===")
        return audio_buffer
        
    except Exception as e:
        logger.error(f"Error in main audio generation process: {str(e)}")
        raise

# if __name__ == "__main__":
#     main(0)