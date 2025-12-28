"""
=========================================================
🔥 MULTI PROVIDER LLM — PLAN C (DIRECT GOOGLE LINK) 🔥
=========================================================
"""
import os
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
        'openai': {'name': 'OpenAI (Disabled)', 'priority': 2},
        'gemini': {'name': 'Google Gemini', 'priority': 3},
        'ollama': {'name': 'Ollama (Local)', 'priority': 4}
    }

    def __init__(self, temperature: float = 0.7):
        self.temperature = temperature
        self.providers_available = self._check_available_providers()

    def _check_available_providers(self):
        available = []
        if os.getenv('GROQ_API_KEY'): available.append('groq')
        if os.getenv('GOOGLE_API_KEY'): available.append('gemini')
        available.append('ollama') 
        return available

    # ---------- GROQ ----------
    def groq(self):
        return LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=self.temperature,
        )

    # ---------- GOOGLE GEMINI (DIRECT LINK) ----------
    def gemini(self):
        """
        Uses ChatGoogleGenerativeAI to bypass LiteLLM entirely.
        """
        if HAS_LANGCHAIN_GOOGLE:
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=self.temperature,
                convert_system_message_to_human=True 
            )
        else:
            return LLM(
                model="gemini-3-flash-preview",
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=self.temperature
            )

    # ---------- OLLAMA (LOCAL) ----------
    def ollama(self):
        return LLM(
            model="ollama/llama3.1",
            base_url="http://localhost:11434",
            temperature=self.temperature,
        )


# ================================================================
# 🧠 AGENT-SPECIFIC ASSIGNMENTS
# ================================================================

def get_planner_llm():
    return MultiProviderLLM(temperature=0.1).groq()

def get_researcher_llm():
    return MultiProviderLLM(temperature=0.3).groq()

def get_extractor_llm():
    return MultiProviderLLM(temperature=0.1).ollama()

def get_fact_checker_llm():
    return MultiProviderLLM(temperature=0.1).ollama()

def get_summarizer_llm():
    return MultiProviderLLM(temperature=0.2).ollama()

def get_writer_llm():
    google_key = os.getenv("GOOGLE_API_KEY", "")
    if google_key and google_key.startswith("AIza"):
        print("✅ Using Direct Gemini Connection")
        return MultiProviderLLM(temperature=0.7).gemini()
    return MultiProviderLLM(temperature=0.7).groq()


# ================================================================
# 🔧 GENERIC HELPERS
# ================================================================

def get_groq_llm(temperature=0.7): return MultiProviderLLM(temperature).groq()
def get_gemini_llm(temperature=0.7): return MultiProviderLLM(temperature).gemini()
def get_ollama_llm(temperature=0.7): return MultiProviderLLM(temperature).ollama()