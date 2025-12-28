import streamlit as st
import os
import sys
import time
import base64
from datetime import datetime
from dotenv import load_dotenv

# =========================================================
# 🛡️ ROBUST SETUP: KEY LOADING & OPENAI "MASQUERADE"
# =========================================================
# This section MUST run before any other project imports.

if hasattr(st, "secrets"):
    # We explicitly check each key to ensure they are loaded correctly
    # 1. DeepSeek (Logic)
    if "DEEPSEEK_API_KEY" in st.secrets:
        os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]
        
    # 2. OpenRouter / Qwen (Writing)
    if "OPENROUTER_API_KEY" in st.secrets:
        os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
        
    # 3. Google Gemini (Context/PDFs)
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
        
    # 4. Search Tools
    if "TAVILY_API_KEY" in st.secrets:
        os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
    if "SERPER_API_KEY" in st.secrets:
        os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]
        
    # 5. Groq (Backup)
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# --- 🛑 THE FIX: FORCE DEEPSEEK AS SYSTEM DEFAULT ---
# This prevents the "OpenAI 401" error by redirecting system calls
if os.getenv("DEEPSEEK_API_KEY"):
    # ✅ OPTION A: DeepSeek V3 (Primary)
    os.environ["OPENAI_API_KEY"] = os.environ["DEEPSEEK_API_KEY"]
    os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com"
    os.environ["OPENAI_MODEL_NAME"] = "deepseek-chat"
    
elif os.getenv("OPENROUTER_API_KEY"):
    # ✅ OPTION B: OpenRouter/Qwen (Backup)
    os.environ["OPENAI_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    os.environ["OPENAI_MODEL_NAME"] = "qwen/qwen-2.5-72b-instruct"
    
elif os.getenv("GROQ_API_KEY"):
    # ⚠️ OPTION C: Groq (Emergency)
    os.environ["OPENAI_API_KEY"] = os.environ["GROQ_API_KEY"]
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"

else:
    # Last Resort
    os.environ["OPENAI_API_KEY"] = "NA"

# Disable Telemetry
os.environ["OTEL_SDK_DISABLED"] = "true" 
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

load_dotenv()

# ---------------------------------------------------
# 🚨 IMPORTS (MUST BE AFTER CONFIGURATION)
# ---------------------------------------------------
from src.crew.research_crew import ResearchCrew
from src.llm.multi_provider import MultiProviderLLM
from src.translation import get_supported_languages
from src.database import get_all_research, get_research_by_id, delete_research_record
from src.audio.stt import speech_to_text
from src.utils.media_factory import generate_multilingual_assets
from fpdf import FPDF
from gtts import gTTS

# Page config
st.set_page_config(
    page_title="AutoResearch Crew Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- UTILITY FUNCTIONS ---
def display_pdf_preview(file_path):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not preview PDF: {e}")

def generate_pdf(text, filename):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # Unicode Safety
        clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
        clean_text = clean_text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2019', "'")
        pdf.multi_cell(0, 10, clean_text)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        pdf.output(filename)
        return filename
    except Exception as e:
        st.warning(f"Note: PDF generated with some character omissions. ({str(e)})")
        return None

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main-header { font-size: 3rem; font-weight: bold; background: linear-gradient(120deg, #6a11cb, #2575fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 1rem; }
    .sub-header { font-size: 1.2rem; color: #666; text-align: center; margin-bottom: 2rem; }
    .stButton>button { width: 100%; background: linear-gradient(120deg, #6a11cb, #2575fc); color: white; border: none; padding: 0.75rem; border-radius: 8px; transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(106, 17, 203, 0.3); }
    .stCodeBlock { background-color: #0e1117 !important; border-radius: 10px; border: 1px solid #30363d; color: #d1d5db; }
    </style>
""", unsafe_allow_html=True)

if 'research_topic' not in st.session_state:
    st.session_state.research_topic = ""

# Header
st.markdown('<div class="main-header">🧠 AutoResearch Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by DeepSeek V3, Qwen 2.5 & Gemini • Hybrid Architecture</div>', unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Engine Status")
    
    # Live Key Check
    key_status = {
        "DeepSeek (Logic)": bool(os.getenv("DEEPSEEK_API_KEY")),
        "Qwen (Writer)": bool(os.getenv("OPENROUTER_API_KEY")),
        "Gemini (Reader)": bool(os.getenv("GOOGLE_API_KEY")),
        "Tavily (Search)": bool(os.getenv("TAVILY_API_KEY"))
    }
    
    # Display Status Icons
    for provider, is_active in key_status.items():
        if is_active:
            st.write(f"✅ **{provider}**")
        else:
            st.write(f"❌ **{provider}**")

    # Critical Warning
    if not any(key_status.values()):
        st.error("❌ Critical: No AI Models available! Check Streamlit Secrets.")

    st.divider()
    page = st.radio("📑 Navigation", ["🔍 New Research", "📚 Research History", "🎤 Voice Input", "⚙️ Settings"])

# --- MAIN CONTENT ---
if page == "🔍 New Research":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header("🔍 Research Topic")
        use_voice = st.checkbox("🎤 Live Voice Input", value=False)
        if use_voice:
            audio_data = st.audio_input("Speak topic:")
            if audio_data:
                with st.spinner("Transcribing..."):
                    st.session_state.research_topic = speech_to_text(audio_data.read())
                    st.success("Transcribed!")

        topic = st.text_input("Enter Topic:", value=st.session_state.research_topic, placeholder="e.g. Future of Solid State Batteries")

        # Quick Start Buttons
        st.caption("💡 **Quick Examples:**")
        ex_cols = st.columns(3)
        if ex_cols[0].button("Quantum Computing"):
            st.session_state.research_topic = "Quantum Computing Applications"
            st.rerun()
        if ex_cols[1].button("AI in Medicine"):
            st.session_state.research_topic = "AI Agents in Healthcare"
            st.rerun()
        if ex_cols[2].button("Mars Terraforming"):
            st.session_state.research_topic = "Feasibility of Mars Terraforming"
            st.rerun()

    with col2:
        st.header("🎯 Settings")
        all_langs = get_supported_languages()
        
        main_langs = {k:v for k,v in all_langs.items() if k in ['English', 'Hindi', 'Spanish', 'French', 'Arabic', 'German', 'Japanese', 'Chinese']}
        if not main_langs:
            main_langs = {'English': 'en'}
        
        sel_lang_name = st.selectbox("Language", list(main_langs.keys()))
        sel_lang_code = main_langs[sel_lang_name]

        export_pdf = st.checkbox("Export PDF", value=True)

    st.divider()

    # --- EXECUTION LOOP ---
    if st.button("🚀 Start Deep Research", type="primary"):
        if not topic:
            st.error("Please provide a research topic.")
        else:
            try:
                # Thread-safe Status Container
                with st.status("🤖 Orchestrating AI Agents...", expanded=True) as s:
                    st.write("🧠 **Planner (Qwen):** Designing research strategy...")
                    st.write("🕵️ **Researcher (DeepSeek):** Scouring the web...")
                    st.write("🧐 **Analyst (DeepSeek):** Verifying data patterns...")
                    st.write("✅ **Fact Checker (DeepSeek):** Validating information...")
                    st.write("✍️ **Writer (Qwen):** Drafting final report...")
                    
                    # Initialize Crew
                    crew = ResearchCrew(topic, sel_lang_code)
                    results = crew.run()
                    
                    s.update(label="✅ Mission Complete!", state="complete", expanded=False)

                if results and 'report_path' in results:
                    st.success("Research Successfully Completed!")
                    
                    # Generate Media Assets (Translations/Audio)
                    with st.spinner("Generating Multilingual Assets..."):
                        assets = generate_multilingual_assets(results['report_path'])

                    # Display Tabs
                    t1, t2, t3 = st.tabs(["📝 Final Report", "📄 PDF Document", "🌍 Multilingual Hub"])
                    
                    # Tab 1: Markdown
                    with t1:
                        if os.path.exists(results['report_path']):
                            with open(results['report_path'], 'r', encoding='utf-8') as f:
                                markdown_text = f.read()
                            st.markdown(markdown_text)
                            st.download_button("Download Markdown", markdown_text, file_name="report.md")

                    # Tab 2: PDF
                    with t2:
                        if export_pdf:
                            pdf_path = results['report_path'].replace(".md", ".pdf")
                            if not os.path.exists(pdf_path):
                                generate_pdf(markdown_text, pdf_path)
                            
                            if os.path.exists(pdf_path):
                                display_pdf_preview(pdf_path)
                                with open(pdf_path, "rb") as f:
                                    st.download_button("Download PDF Report", f, file_name="report.pdf")
                            else:
                                st.warning("PDF generation failed.")
                        else:
                            st.info("PDF Export disabled.")

                    # Tab 3: Multilingual & Audio
                    with t3:
                        if assets:
                            l_key = st.selectbox("Select Output Language", list(assets.keys()))
                            data = assets[l_key]
                            
                            c1, c2 = st.columns(2)
                            with c1: 
                                st.subheader("🎧 Audio")
                                if os.path.exists(data['audio_path']): 
                                    st.audio(data['audio_path'])
                                    with open(data['audio_path'], "rb") as f:
                                        st.download_button("Download Audio", f, file_name=f"audio_{l_key}.mp3")
                                else:
                                    st.info("Audio unavailable.")
                                
                            with c2:
                                st.subheader("📄 Report")
                                if os.path.exists(data['report_path']):
                                    with open(data['report_path'], 'rb') as f:
                                        st.download_button(f"Download {l_key} Text", f, file_name=f"report_{l_key}.md")
                                else:
                                    st.info("Translation unavailable.")
                            
                            st.divider()
                            st.text_area("Translation Preview", data['text'], height=200)
                        else:
                            st.warning("Multilingual assets not available.")

            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

# --- HISTORY PAGE ---
elif page == "📚 Research History":
    st.header("Archives")
    history = get_all_research(limit=10)
    if history:
        for h in history:
            with st.expander(f"📅 {h.created_at.strftime('%Y-%m-%d %H:%M')} - {h.topic}"):
                st.write(f"**Status:** {h.status}")
                if h.report_path and os.path.exists(h.report_path):
                    with open(h.report_path, 'r', encoding='utf-8') as f:
                        st.text_area("Snippet", f.read()[:300]+"...", height=100)
    else:
        st.info("No history found.")

# --- SETTINGS PAGE ---
elif page == "⚙️ Settings":
    st.header("System Configuration")
    st.json(key_status)
    st.write("---")
    st.write("**Architecture:** Hybrid Cloud (DeepSeek + Qwen + Gemini)")
    st.write("**Version:** 2.2.0 (Writer-Last Edition)")

st.divider()
st.markdown("<center>AutoResearch Crew Pro • 2025 Architecture</center>", unsafe_allow_html=True)