"""
=========================================================
🔥 MULTI PROVIDER LLM — CLOUD DEPLOYMENT MODE (RATE LIMITED) 🔥
=========================================================
"""
import os
import time
from crewai import LLM

# --- 1. NUCLEAR SANITIZER ---
if "OPENAI_API_KEY" in os.environ:
    del os.environ["OPENAI_API_KEY"]
os.environ["LITELLM_DISABLE_OPENAI"] = "true"

# --- 2. IMPORT DIRECT GOOGLE CONNECTOR ---
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    HAS_LANGCHAIN_GOOGLE = True
except ImportError:
    HAS_LANGCHAIN_GOOGLE = False

class MultiProviderLLM:
    
    PROVIDERS = {
        'groq': {'name': 'Groq (Llama 3)', 'priority': 1},
        'gemini': {'name': 'Google Gemini', 'priority': 2},
    }

    def __init__(self, temperature: float = 0.7):
        self.temperature = temperature

    # ---------- GROQ (With Rate Limit Protection) ----------
    def groq(self):
        return LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=self.temperature,
            max_retries=3,
            timeout=120
        )

    # ---------- GOOGLE GEMINI (The "Backup Tank") ----------
    def gemini(self):
        if HAS_LANGCHAIN_GOOGLE:
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=self.temperature,
                convert_system_message_to_human=True 
            )
        else:
            return LLM(
                model="gemini/gemini-3-flash-preview",
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=self.temperature
            )

# ================================================================
# 🧠 AGENT-SPECIFIC ASSIGNMENTS (The "Hybrid" Strategy)
# ================================================================

def get_planner_llm():
    return MultiProviderLLM(temperature=0.1).groq()

def get_researcher_llm():
    return MultiProviderLLM(temperature=0.3).groq()

def get_extractor_llm():
    print("🔄 Routing Heavy Extraction Task to Google Gemini (High Volume)")
    return MultiProviderLLM(temperature=0.1).gemini()

def get_fact_checker_llm():
    return MultiProviderLLM(temperature=0.1).groq()

def get_summarizer_llm():
    return MultiProviderLLM(temperature=0.2).gemini()

def get_writer_llm():
    return MultiProviderLLM(temperature=0.7).groq()

# ================================================================
# 🚑 LEGACY HELPERS (Restored to fix ImportErrors)
# ================================================================

def get_gemini_llm(temperature=0.7):
    """Helper used by SummarizerAgent and others directly"""
    return MultiProviderLLM(temperature).gemini()

def get_groq_llm(temperature=0.7):
    """Helper used by generic agents"""
    return MultiProviderLLM(temperature).groq()