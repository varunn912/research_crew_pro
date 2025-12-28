import os
from gtts import gTTS
from deep_translator import GoogleTranslator
import streamlit as st

def generate_multilingual_assets(report_path):
    """
    Robustly generates translated text and audio for 5 languages.
    SAFE MODE: If any language fails, it skips it without crashing the app.
    """
    results = {}
    
    # 1. Validation: Ensure the source report actually exists
    if not os.path.exists(report_path):
        return None
        
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            english_text = f.read()
    except Exception as e:
        print(f"Error reading report: {e}")
        return None

    # 2. Define User-Requested Languages
    # (Code, Display Name)
    languages = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('ar', 'Arabic'),
        ('es', 'Spanish'),
        ('fr', 'French')
    ]

    # 3. Process Each Language Independently
    for lang_code, lang_name in languages:
        try:
            # --- A. TRANSLATION (With Chunking for Safety) ---
            if lang_code == 'en':
                text_content = english_text
            else:
                # Split by double newlines to keep paragraphs intact
                chunks = [chunk for chunk in english_text.split('\n\n') if chunk]
                translated_chunks = []
                translator = GoogleTranslator(source='auto', target=lang_code)
                
                for chunk in chunks:
                    if len(chunk.strip()) > 0:
                        try:
                            # Limit chunk size to 4500 to stay under API limits
                            trans = translator.translate(chunk[:4500]) 
                            translated_chunks.append(trans)
                        except Exception as e:
                            # Fallback: If translation fails, keep original text
                            print(f"Translation chunk error ({lang_code}): {e}")
                            translated_chunks.append(chunk) 
                
                text_content = '\n\n'.join(translated_chunks)

            # --- B. SAVE REPORT FILE (The "PDF" Equivalent) ---
            # We save as .md because generating PDFs with Hindi/Arabic fonts 
            # often crashes Python. Markdown is safer and universal.
            os.makedirs("output", exist_ok=True)
            report_filename = f"report_{lang_code}.md"
            report_file_path = os.path.join("output", report_filename)
            
            with open(report_file_path, "w", encoding="utf-8") as f:
                f.write(text_content)

            # --- C. AUDIO GENERATION (gTTS) ---
            audio_filename = f"audio_{lang_code}.mp3"
            audio_path = os.path.join("output", audio_filename)
            
            # gTTS is robust. We limit text to 3000 chars to ensure speed.
            if text_content.strip():
                tts = gTTS(text=text_content[:3000], lang=lang_code) 
                tts.save(audio_path)

            # Store successful paths
            results[lang_name] = {
                "text": text_content,
                "audio_path": audio_path,
                "report_path": report_file_path 
            }
            
        except Exception as e:
            # This print ensures you see the error in logs, but the User UI does not crash
            print(f"⚠️ Error processing language {lang_name}: {e}")
            continue # Skip to next language
            
    return results