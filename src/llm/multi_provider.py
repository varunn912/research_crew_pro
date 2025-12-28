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
        # We use a slightly smaller model for the Extractor to save TPM if needed
        # But here we stick to the versatile one and rely on system pauses
        return LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=self.temperature,
            max_retries=3, # Auto-retry on 429 errors
            timeout=120
        )

    # ---------- GOOGLE GEMINI (The "Backup Tank") ----------
    # Gemini Flash has a much higher TPM limit (1M tokens/min on free tier sometimes)
    # We should use THIS for the heavy lifting (Extractor)
    def gemini(self):
        if HAS_LANGCHAIN_GOOGLE:
            return ChatGoogleGenerativeAI(
                model="gemini-3-flash-preview",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=self.temperature,
                convert_system_message_to_human=True 
            )
        else:
            return LLM(
                model="gemini/gemini-1.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=self.temperature
            )

# ================================================================
# 🧠 AGENT-SPECIFIC ASSIGNMENTS (The "Hybrid" Strategy)
# ================================================================

def get_planner_llm():
    # Planner needs reasoning -> Groq
    return MultiProviderLLM(temperature=0.1).groq()

def get_researcher_llm():
    # Researcher makes short queries -> Groq
    return MultiProviderLLM(temperature=0.3).groq()

def get_extractor_llm():
    # ⚠️ EXTRACTOR READS HUGE TEXT -> USE GEMINI
    # Gemini 1.5 Flash has a massive context window and high limits.
    # It is perfect for reading websites without crashing Groq.
    print("🔄 Routing Heavy Extraction Task to Google Gemini (High Volume)")
    return MultiProviderLLM(temperature=0.1).gemini()

def get_fact_checker_llm():
    # Fact checker reads summaries -> Groq is fine
    return MultiProviderLLM(temperature=0.1).groq()

def get_summarizer_llm():
    return MultiProviderLLM(temperature=0.2).gemini() # Summarizing is heavy -> Gemini

def get_writer_llm():
    # Writer uses Groq Direct Link (already handled in research_crew.py)
    return MultiProviderLLM(temperature=0.7).groq()