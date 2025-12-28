import os
import openai
import groq
import io
from typing import Optional

# --- Client Initialization ---
# We initialize both clients. They will automatically read the keys from .env

# Initialize Groq Client
try:
    groq_client = groq.Groq()
    groq_api_valid = True
    print("Groq client initialized.")
except Exception as e:
    print(f"Warning: Groq client could not be initialized. {e}")
    groq_client = None
    groq_api_valid = False

# Initialize OpenAI Client
try:
    openai_client = openai.OpenAI()
    openai_api_valid = True
    print("OpenAI client initialized.")
except Exception as e:
    print(f"Warning: OpenAI client could not be initialized. {e}")
    openai_client = None
    openai_api_valid = False


def speech_to_text(audio_bytes: bytes, language: str = 'en') -> Optional[str]:
    """
    Convert speech audio bytes to text using a primary (Groq) and fallback (OpenAI) API.
    This version fails fast on authentication errors.
    """
    
    # Create a file-like object from the in-memory audio bytes
    try:
        audio_io = io.BytesIO(audio_bytes)
        audio_io.name = "audio.webm" 
    except Exception as e:
        print(f"❌ Error creating audio buffer: {e}")
        return f"Error processing audio data: {e}"

    groq_error = None
    openai_error = None

    # --- Try Groq First (Primary) ---
    if groq_api_valid:
        print("Attempting transcription with Groq...")
        try:
            audio_io.seek(0) # Reset buffer
            transcription = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=("audio.webm", audio_io.read()),
                language=language
            )
            print("✅ Groq transcription successful.")
            return transcription.text
        
        except groq.AuthenticationError:
            print("❌ Groq Authentication Error.")
            # This is a fatal error for Groq. Stop and report it.
            return "Error: Groq Authentication Error. Check GROQ_API_KEY."
        except groq.RateLimitError as e:
            print("⚠️ Groq Rate Limit Error. Trying OpenAI...")
            groq_error = "Groq rate limit exceeded."
        except Exception as e:
            print(f"⚠️ Groq STT error: {e}. Trying OpenAI...")
            groq_error = str(e)
    
    # --- Try OpenAI Second (Fallback) ---
    # This block will run if Groq is not valid OR if it failed with a non-auth error
    if openai_api_valid:
        print("Attempting transcription with OpenAI...")
        try:
            audio_io.seek(0) # Reset buffer
            transcription = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_io,
                language=language
            )
            print("✅ OpenAI transcription successful.")
            return transcription.text
            
        except openai.AuthenticationError:
            print("❌ OpenAI Authentication Error.")
            # This is a fatal error for OpenAI. Stop and report it.
            return "Error: OpenAI Authentication Error. Check OPENAI_API_KEY."
        except openai.RateLimitError as e:
            print("❌ OpenAI Rate Limit Error (Quota Exceeded).")
            # This is the error you are seeing
            return "Error: OpenAI Quota Exceeded. Please check billing."
        except Exception as e:
            print(f"❌ OpenAI STT error: {e}")
            openai_error = str(e)

    # --- If both fail ---
    print("❌ Both Groq and OpenAI transcription failed.")
    if not groq_api_valid and not openai_api_valid:
        return "Error: No speech-to-text API keys are configured (Groq or OpenAI)."
    
    # Return the most specific error we have
    if openai_error:
        return f"OpenAI Error: {openai_error}"
    if groq_error:
        return f"Groq Error: {groq_error}"
        
    return "Error: Transcription failed for all available services."


# --- Keep your other functions ---
# They will automatically use the new resilient `speech_to_text` function above.

def speech_to_text_gemini(audio_file: str, language: str = 'en-US') -> Optional[str]:
    """
    (This function is no longer the primary one, but we keep it
    and adapt it to use the new bytes-based function)
    """
    try:
        with open(audio_file, 'rb') as f:
            audio_bytes = f.read()
        return speech_to_text(audio_bytes, language.split('-')[0])
    except Exception as e:
        print(f"❌ STT error: {e}")
        return None

def transcribe_audio_file(audio_path: str, language: str = 'en-US') -> Optional[str]:
    """Transcribe audio file and save as text."""
    try:
        text = speech_to_text_gemini(audio_path, language)
        
        if text and not text.startswith("Error:"):
            # Save transcription
            text_path = audio_path.replace('.wav', '.txt').replace('.mp3', '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"✅ Transcription saved: {text_path}")
            return text
        
        return text # Return the error message if transcription failed
        
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None