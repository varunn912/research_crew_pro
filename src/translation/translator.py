from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory
from typing import Optional, Dict, List
import time

# Set seed for consistent language detection
DetectorFactory.seed = 0

# --- FINALIZED TOP 5 LANGUAGES ---
# Optimized for high-quality NotoSans PDF rendering and gTTS Audio
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'ar': 'Arabic',
    'es': 'Spanish',
    'fr': 'French'
}

def get_supported_languages() -> Dict[str, str]:
    """Get dictionary of the 5 supported languages."""
    return SUPPORTED_LANGUAGES

def detect_language(text: str) -> str:
    """Detect the language of the text with safety fallback."""
    try:
        if not text or len(text.strip()) < 5:
            return 'en'
        return detect(text)
    except Exception as e:
        # Default to English if detection fails
        return 'en'

def translate_text(
    text: str,
    target_language: str,
    source_language: str = 'auto'
) -> str:
    """
    Translate text to target language using deep-translator.
    Implements a 'Relay' chunking strategy to avoid Google API timeouts.
    """
    try:
        # Handle empty text
        if not text or not text.strip():
            return text

        # 1. Auto-detect source language if needed
        actual_source = source_language
        if source_language == 'auto':
            actual_source = detect_language(text)
            
        # 2. Critical Check: Skip if already in target language
        if actual_source == target_language:
            return text
            
        # 3. Setup Translator
        translator = GoogleTranslator(source=actual_source, target=target_language)
        
        # 4. Smart Chunking (Standard 5000 limit, using 3500 for safety)
        # We split by double newlines to keep paragraphs intact for the PDF generator
        max_chars = 3500 
        
        if len(text) <= max_chars:
            return translator.translate(text)
        
        # Split into paragraphs to maintain Markdown structure
        paragraphs = text.split('\n\n')
        translated_paragraphs = []
        current_chunk = ""

        for p in paragraphs:
            if len(current_chunk) + len(p) < max_chars:
                current_chunk += p + "\n\n"
            else:
                # Translate the accumulated chunk
                if current_chunk.strip():
                    translated_paragraphs.append(translator.translate(current_chunk.strip()))
                    # Tiny sleep to avoid Google rate-limiting
                    time.sleep(0.5) 
                current_chunk = p + "\n\n"

        # Translate final chunk
        if current_chunk.strip():
            translated_paragraphs.append(translator.translate(current_chunk.strip()))

        final_result = '\n\n'.join(translated_paragraphs)
        
        # 5. Markdown Safety check
        # Ensures headers (#) and bold (**) aren't broken by the translator's spaces
        final_result = final_result.replace('# # #', '###').replace('# #', '##')
        
        return final_result
        
    except Exception as e:
        print(f"⚠️ Translation Critical Failure: {e}")
        # ROBUSTNESS: Never crash the app, return original text if translation fails
        return text

def batch_translate(
    texts: List[str],
    target_language: str,
    source_language: str = 'auto'
) -> List[str]:
    """Translate multiple text blocks sequentially."""
    translated = []
    for text in texts:
        translated.append(translate_text(text, target_language, source_language))
    return translated