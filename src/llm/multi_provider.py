import os
from crewai import LLM
from langchain_google_genai import ChatGoogleGenerativeAI

class MultiProviderLLM:
    def __init__(self, temperature=0.7):
        self.temperature = temperature
        self.providers_available = []
        
        # --- UI METADATA (Used by app.py sidebar) ---
        self.PROVIDERS = {
            "deepseek": {"name": "DeepSeek V3 (Logic)", "priority": 1},
            "qwen": {"name": "Qwen 2.5 (Creative)", "priority": 1},
            "gemini": {"name": "Google Gemini (Context)", "priority": 2},
            "groq": {"name": "Groq Llama 3 (Backup)", "priority": 3}
        }
        
        # 1. Check availability of all keys
        if os.getenv("DEEPSEEK_API_KEY"): self.providers_available.append("deepseek")
        if os.getenv("OPENROUTER_API_KEY"): self.providers_available.append("qwen")
        if os.getenv("GOOGLE_API_KEY"): self.providers_available.append("gemini")
        if os.getenv("GROQ_API_KEY"): self.providers_available.append("groq")

    # --- 1. DEEPSEEK V3 (Logic Core) ---
    def deepseek(self):
        return LLM(
            model="openai/deepseek-chat",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
            temperature=self.temperature
        )

    # --- 2. QWEN 2.5 (Creative Core) ---
    def qwen(self):
        return LLM(
            model="openai/qwen/qwen-2.5-72b-instruct",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
            temperature=self.temperature
        )

    # --- 3. GEMINI (Context Core) ---
    def gemini(self):
        return ChatGoogleGenerativeAI(
            model="gemini-3-flash-preview",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=self.temperature
        )

    # --- 4. GROQ (Speed/Backup Core) ---
    def groq(self):
        return LLM(
            model="groq/llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=self.temperature
        )

# ================================================================
# 🧠 ROBUST AGENT MAPPING (Waterfall Logic)
# ================================================================

def _get_best_available(llm_instance, preferred_order):
    """
    Helper: Iterates through preferences and returns the first available.
    """
    for provider in preferred_order:
        if provider in llm_instance.providers_available:
            if provider == "deepseek": return llm_instance.deepseek()
            if provider == "qwen": return llm_instance.qwen()
            if provider == "gemini": return llm_instance.gemini()
            if provider == "groq": return llm_instance.groq()
    
    # Critical Fallback: Use Groq if preferred models failed
    if "groq" in llm_instance.providers_available:
        print("⚠️ Warning: Preferred models unavailable. Falling back to Groq.")
        return llm_instance.groq()
    
    # Absolute Last Resort: Check if Gemini is there
    if "gemini" in llm_instance.providers_available:
        return llm_instance.gemini()
        
    raise Exception("❌ No LLM providers available! Please check Streamlit Secrets.")

def get_planner_llm():
    # 🧠 PLANNER: Needs structure -> Qwen > DeepSeek > Groq
    llm = MultiProviderLLM(temperature=0.6)
    return _get_best_available(llm, ["qwen", "deepseek", "groq"])

def get_researcher_llm():
    # 🕵️ RESEARCHER: Needs speed & logic -> DeepSeek > Qwen > Groq
    llm = MultiProviderLLM(temperature=0.3)
    return _get_best_available(llm, ["deepseek", "qwen", "groq"])

def get_extractor_llm():
    # 📄 EXTRACTOR: Needs massive context -> Gemini > Qwen > DeepSeek > Groq
    llm = MultiProviderLLM(temperature=0.1)
    return _get_best_available(llm, ["gemini", "qwen", "deepseek", "groq"])

def get_summarizer_llm():
    # 📝 SUMMARIZER: Needs conciseness -> Qwen > Gemini > Groq
    llm = MultiProviderLLM(temperature=0.2)
    return _get_best_available(llm, ["qwen", "gemini", "groq"])

def get_fact_checker_llm():
    # ✅ FACT CHECKER: Needs strict logic -> DeepSeek > Qwen > Groq
    llm = MultiProviderLLM(temperature=0.1)
    return _get_best_available(llm, ["deepseek", "qwen", "groq"])

def get_analyst_llm():
    # 📈 ANALYST: Needs pattern recognition -> DeepSeek > Qwen > Groq
    llm = MultiProviderLLM(temperature=0.4)
    return _get_best_available(llm, ["deepseek", "qwen", "groq"])

def get_writer_llm():
    # ✍️ WRITER: Needs human tone -> Qwen > DeepSeek > Groq
    llm = MultiProviderLLM(temperature=0.7)
    return _get_best_available(llm, ["qwen", "deepseek", "groq"])

# --- REDIRECTS (Legacy Support) ---
def get_gemini_llm(t=0.7): 
    llm = MultiProviderLLM(t)
    return _get_best_available(llm, ["gemini", "qwen", "groq"])

def get_groq_llm(t=0.7): 
    llm = MultiProviderLLM(t)
    return _get_best_available(llm, ["groq", "qwen", "deepseek"])

def get_ollama_llm(t=0.7): 
    llm = MultiProviderLLM(t)
    return _get_best_available(llm, ["deepseek", "qwen", "groq"])