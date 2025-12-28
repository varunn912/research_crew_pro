from .translator import translate_text, detect_language, get_supported_languages
from .pdf_generator import generate_multilingual_pdf

__all__ = [
    'translate_text',
    'detect_language',
    'get_supported_languages',
    'generate_multilingual_pdf'
]