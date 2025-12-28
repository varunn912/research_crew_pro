import os
from datetime import datetime
from typing import Optional
from gtts import gTTS
from gtts.lang import tts_langs

# --- 1. LANGUAGE CONFIGURATION ---
# These match your translation/PDF module exactly
SUPPORTED_AUDIO_LANGS = ['en', 'hi', 'ar', 'es', 'fr']

def text_to_speech_pro(
    text: str,
    output_path: Optional[str] = None,
    language: str = 'en'
) -> Optional[str]:
    """
    Convert text to speech using gTTS with professional scrubbing.
    """
    # Validate language support
    try:
        supported = tts_langs()
        if language not in supported or language not in SUPPORTED_AUDIO_LANGS:
            print(f"⚠️ Audio skipped: Language '{language}' is not in the professional support list.")
            return None
    except Exception:
        # Fallback if gTTS language list is unreachable
        if language not in SUPPORTED_AUDIO_LANGS:
            return None

    try:
        # Ensure professional output directory exists
        os.makedirs('output/audio', exist_ok=True)
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/audio/research_voice_{timestamp}.mp3"

        # --- PROFESSIONAL TEXT SCRUBBING ---
        # 1. Limit length for stability (gTTS standard limit is ~5000 chars)
        if len(text) > 4500:
            text = text[:4500] + "... This concludes the audio summary."

        # 2. Markdown Scrubber: Ensure the voice doesn't read "hashtag hashtag" or "asterisk"
        # Removes headers, bold, italics, and code blocks
        clean_text = text.replace('#', '').replace('*', '').replace('_', '').replace('`', '')
        # Remove extra whitespace
        clean_text = " ".join(clean_text.split())

        if not clean_text.strip():
            return None

        # 3. Generate Speech
        tts = gTTS(text=clean_text, lang=language, slow=False)
        tts.save(output_path)

        # 4. Final Verification
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            print(f"✅ Professional Audio Ready: {output_path}")
            return output_path
        else:
            return None

    except Exception as e:
        print(f"❌ TTS Engine Failure: {e}")
        return None

def generate_report_audio(
    report_path: str,
    language: str = 'en'
) -> Optional[str]:
    """
    Extracts content from a markdown report and generates a high-quality summary audio.
    """
    try:
        if not os.path.exists(report_path):
            return None

        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract only the body content for audio (skipping metadata lines)
        lines = content.split('\n')
        useful_lines = []
        char_count = 0
        
        for line in lines:
            # Skip empty lines, horizontal rules, and metadata
            if not line.strip() or line.startswith('---') or "Generation Date" in line:
                continue
            
            # Stop if we hit the char limit for gTTS stability
            if char_count > 4000:
                break
                
            useful_lines.append(line.strip())
            char_count += len(line)

        final_body = " ".join(useful_lines)
        
        if len(final_body) < 50:
            final_body = "The research report has been generated successfully. Please refer to the PDF for full details."

        # Professional Intro
        intro = "Research summary. " if language == 'en' else ""
        final_text = intro + final_body

        # Output path matches report filename but in mp3 format
        audio_path = report_path.replace('.md', '.mp3')
        return text_to_speech_pro(final_text, audio_path, language)

    except Exception as e:
        print(f"❌ Report Audio Processing Error: {e}")
        return None

# --- COMPATIBILITY WRAPPERS ---
def text_to_speech(text: str, output_path: Optional[str] = None, language: str = 'en') -> Optional[str]:
    return text_to_speech_pro(text, output_path, language)

def text_to_speech_gemini(text: str, output_path: Optional[str] = None, language: str = 'en') -> Optional[str]:
    return text_to_speech_pro(text, output_path, language)