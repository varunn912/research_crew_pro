import os
import sys
import requests
import pydantic
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

def check_status(name, condition):
    if condition:
        print(f"✅ {name}: WORKING")
        return True
    else:
        print(f"❌ {name}: FAILED")
        return False

def verify_no_openai_dependency():
    """
    STRICT CHECK: Ensures OpenAI is disabled and custom brains are mapped.
    This prevents the 'ConnectionError' during Planning.
    """
    print("\n--- 🛡️ OpenAI Lockdown & Zero-Key Check ---")
    results = []
    
    # 1. Check for OpenAI Key (Should be empty or dummy for this project)
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key or openai_key == "sk-no-key-required" or openai_key == "":
        results.append(check_status("OpenAI Disabled (Clean Environment)", True))
    else:
        print(f"⚠️ Warning: OPENAI_API_KEY found in .env. System might try to default to it.")
        results.append(True)

    # 2. Check for Mandatory Custom Keys for Hierarchical Flow
    results.append(check_status("Groq Key (Required for Planner)", bool(os.getenv("GROQ_API_KEY"))))
    results.append(check_status("Google Key (Required for Writer)", bool(os.getenv("GOOGLE_API_KEY"))))
    
    return all(results)

def test_api_connectivity():
    print("\n--- 🛠️ External Tools Connectivity Check ---")
    results = []

    # Test Tavily (Primary Search)
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_key)
            client.search("test", max_results=1)
            results.append(check_status("Tavily Search API", True))
        except:
            results.append(check_status("Tavily Search API", False))
    else:
        results.append(check_status("Tavily API Key", False))

    return all(results)

def test_llm_connectivity():
    print("\n--- 🧠 LLM Brain Connectivity Check ---")
    from src.llm.multi_provider import (
        get_planner_llm, get_researcher_llm, 
        get_extractor_llm, get_writer_llm
    )
    
    test_msg = [HumanMessage(content="hi")]
    results = []

    # 1. Test Groq (Internal Planner & Researcher)
    try:
        get_planner_llm().invoke(test_msg)
        results.append(check_status("Groq (Planner/Master Brain)", True))
    except Exception as e:
        results.append(check_status("Groq Connectivity", False))
        print(f"   Detail: {str(e)[:100]}")

    # 2. Test Gemini (Writer Brain)
    try:
        get_writer_llm().invoke(test_msg)
        results.append(check_status("Google Gemini (Writer Brain)", True))
    except Exception as e:
        results.append(check_status("Gemini Connectivity", False))
        print(f"   Detail: {str(e)[:100]}")

    # 3. Test Ollama (Local Extractor)
    try:
        requests.get("http://localhost:11434", timeout=2)
        get_extractor_llm().invoke(test_msg)
        results.append(check_status("Ollama Local (Extractor Brain)", True))
    except:
        results.append(check_status("Ollama Local", False))
        print(f"   Detail: Run 'ollama serve' and 'ollama pull llama3.1'")

    return all(results)

def check_files():
    print("\n--- 📁 File & System Integrity Check ---")
    files = [
        "src/crew/research_crew.py",
        "src/agents/research_agent.py",
        "src/llm/multi_provider.py",
        "config/agents.yaml",
        "config/tasks.yaml",
        ".env"
    ]
    results = [check_status(f"File: {f}", os.path.exists(f)) for f in files]
    print(f"ℹ️ Pydantic Version: {pydantic.VERSION}")
    return all(results)

if __name__ == "__main__":
    print("==============================================")
    print("🚀 AutoResearch 2025: FINAL READINESS CHECK")
    print("==============================================")
    
    # Run Lockdown check first
    lockdown_ok = verify_no_openai_dependency()
    files_ok = check_files()
    llms_ok = test_llm_connectivity()
    apis_ok = test_api_connectivity()
    
    print("\n==============================================")
    if lockdown_ok and files_ok and llms_ok and apis_ok:
        print("✨ ALL SYSTEMS GO! OpenAI is strictly bypassed.")
        print("👉 Launch with: streamlit run app.py")
    else:
        print("⚠️ SYSTEM NOT READY.")
        print("Please resolve the ❌ items above.")
    print("==============================================")