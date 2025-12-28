import os
import io
import google.generativeai as genai
import groq
from typing import Optional

# =========================================================
# 🎙️ ROBUST SPEECH-TO-TEXT (Gemini Primary -> Groq Backup)
# =========================================================

def _transcribe_with_gemini(audio_bytes: bytes) -> str:
    """
    Primary method: Uses Google Gemini 1.5 Flash for transcription.
    Gemini is natively multimodal and handles audio directly.
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise Exception("GOOGLE_API_KEY not found")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Gemini accepts raw audio data blobs
        response = model.generate_content([
            "Transcribe this audio file accurately. Output ONLY the spoken text. Do not add any conversational filler or descriptions.",
            {
                "mime_type": "audio/wav", # Streamlit audio recorder usually outputs WAV-compatible bytes
                "data": audio_bytes
            }
        ])
        
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini STT Failed: {str(e)}")

def _transcribe_with_groq(audio_bytes: bytes, language: str = 'en') -> str:
    """
    Backup method: Uses Groq's Whisper-large-v3 model.
    Extremely fast and accurate backup.
    """
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise Exception("GROQ_API_KEY not found")

        client = groq.Groq(api_key=api_key)
        
        # Create a virtual file for the API
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav" 
        
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            language=language
        )
        return transcription.text
    except Exception as e:
        raise Exception(f"Groq STT Failed: {str(e)}")

def speech_to_text(audio_data, language: str = 'en') -> str:
    """
    Main entry point for Speech-to-Text.
    Accepts either raw bytes or a file path string.
    
    Strategy:
    1. Try Gemini (Primary)
    2. Try Groq (Backup)
    3. Return Error if both fail
    """
    
    # 1. Normalize Input (Convert file path to bytes if necessary)
    audio_bytes = None
    if isinstance(audio_data, str):
        # It's a file path
        if os.path.exists(audio_data):
            with open(audio_data, "rb") as f:
                audio_bytes = f.read()
        else:
            return "❌ Error: Audio file path not found."
    elif isinstance(audio_data, bytes):
        # It's already bytes
        audio_bytes = audio_data
    else:
        return "❌ Error: Invalid audio input format."

    if not audio_bytes:
        return "❌ Error: Empty audio data."

    # 2. Attempt Transcription (Waterfall Logic)
    errors = []

    # --- Attempt 1: Gemini ---
    try:
        # print("🎙️ Attempting Gemini STT...")
        return _transcribe_with_gemini(audio_bytes)
    except Exception as e:
        # print(f"⚠️ Gemini STT failed: {e}")
        errors.append(str(e))

    # --- Attempt 2: Groq ---
    try:
        # print("🎙️ Falling back to Groq STT...")
        return _transcribe_with_groq(audio_bytes, language)
    except Exception as e:
        # print(f"⚠️ Groq STT failed: {e}")
        errors.append(str(e))

    # 3. Final Failure State
    return f"❌ Transcription failed. Errors: {'; '.join(errors)}"

# --- Legacy Compatibility Functions ---
# Keeps the code compatible if other parts call these specific names

def speech_to_text_gemini(audio_file: str, language: str = 'en-US') -> Optional[str]:
    return speech_to_text(audio_file, language.split('-')[0])

def transcribe_audio_file(audio_path: str, language: str = 'en-US') -> Optional[str]:
    result = speech_to_text(audio_path, language.split('-')[0])
    
    if result and not result.startswith("❌"):
        try:
            text_path = os.path.splitext(audio_path)[0] + ".txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(result)
            return result
        except Exception:
            return result # Return text even if saving failed
    return None