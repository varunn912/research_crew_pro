import streamlit as st
import os
import sys
import time
import base64
from datetime import datetime
from dotenv import load_dotenv

# =========================================================
# 🔑 CRITICAL: LOAD SECRETS (ROBUST MODE)
# =========================================================
if hasattr(st, "secrets"):
    # 1. Groq API Key
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
        
    # 2. Google Gemini API Key
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
        
    # 3. Tavily API Key
    if "TAVILY_API_KEY" in st.secrets:
        os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
    
    # 4. Serper API Key
    if "SERPER_API_KEY" in st.secrets:
        os.environ["SERPER_API_KEY"] = st.secrets["SERPER_API_KEY"]

# --- OPTIONAL: Load local .env ---
load_dotenv()

# =========================================================
# 🎭 THE GROQ MASQUERADE (FIX FOR ERROR 401)
# =========================================================
# If CrewAI tries to default to OpenAI, we redirect it to Groq.
# This prevents the "Incorrect API Key" crash by giving it a working path.

if "GROQ_API_KEY" in os.environ:
    os.environ["OPENAI_API_KEY"] = os.environ["GROQ_API_KEY"]
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL_NAME"] = "llama-3.3-70b-versatile"
else:
    # Last resort fallback if Groq is missing (prevents crash, might fail later)
    os.environ["OPENAI_API_KEY"] = "NA"

# --- DISABLE TELEMETRY ---
os.environ["OTEL_SDK_DISABLED"] = "true" 
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

# ---------------------------------------------------
# 🚨 IMPORTS MUST HAPPEN AFTER KEYS ARE LOADED
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

# --- UTILITY: PDF PREVIEW EMBEDDER ---
def display_pdf_preview(file_path):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not preview PDF: {e}")

# --- ROBUST PDF GENERATOR ---
def generate_pdf(text, filename):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
        clean_text = clean_text.replace('\u2013', '-').replace('\u2014', '-').replace('\u2019', "'")
        pdf.multi_cell(0, 10, clean_text)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        pdf.output(filename)
        return filename
    except Exception as e:
        st.warning(f"Note: PDF generated with some character omissions. ({str(e)})")
        return None

# --- ROBUST AUDIO GENERATOR ---
def generate_audio(text, lang='en'):
    try:
        if lang not in ['en', 'es', 'fr', 'pt', 'de']:
            lang = 'en'
        tts = gTTS(text=text[:3000], lang=lang, slow=False)
        audio_path = "output/research_summary.mp3"
        os.makedirs('output', exist_ok=True)
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
        return None

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main-header { font-size: 3rem; font-weight: bold; background: linear-gradient(120deg, #1E88E5, #00BCD4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 1rem; }
    .sub-header { font-size: 1.2rem; color: #666; text-align: center; margin-bottom: 2rem; }
    .stButton>button { width: 100%; background: linear-gradient(120deg, #1E88E5, #00BCD4); color: white; font-size: 1.1rem; padding: 0.75rem; border-radius: 8px; border: none; transition: all 0.3s ease; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3); }
    .stCodeBlock { background-color: #0e1117 !important; border-radius: 10px; border: 1px solid #30363d; color: #d1d5db; }
    </style>
""", unsafe_allow_html=True)

if 'research_topic' not in st.session_state:
    st.session_state.research_topic = ""

# Header
st.markdown('<div class="main-header">🧠 AutoResearch Crew Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">2025 Nuclear Architecture • Sequential Multi-Agent Intelligence</div>', unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration")
    critical_keys = {"Groq": os.getenv('GROQ_API_KEY'), "Google Gemini": os.getenv('GOOGLE_API_KEY'), "Tavily": os.getenv('TAVILY_API_KEY')}
    missing_keys = [k for k, v in critical_keys.items() if not v]
    if not missing_keys: st.success("✅ Environment configured")
    else: st.error(f"❌ Missing: {', '.join(missing_keys)}")

    st.divider()
    page = st.radio("📑 Navigation", ["🔍 New Research", "📚 Research History", "🎤 Voice Input", "⚙️ Settings"])
    
    st.divider()
    
    # --- LLM PROVIDER STATUS ---
    st.header("🤖 LLM Provider Status")
    try:
        llm_manager = MultiProviderLLM()
        active_providers = llm_manager.providers_available 
        if active_providers:
            st.success(f"✅ {len(active_providers)} provider(s) active")
            for p_id in active_providers:
                p_data = llm_manager.PROVIDERS.get(p_id, {"name": p_id.title(), "priority": 0})
                with st.expander(f"🔹 {p_data['name']}"):
                    st.write(f"**Priority:** Level {p_data['priority']}")
                    st.write(f"**Status:** Online")
        else:
            st.error("❌ No LLM providers found.")
    except Exception as e:
        st.warning("Could not check LLM status.")

# --- MAIN CONTENT ---
if page == "🔍 New Research":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.header("🔍 Research Topic")
        use_voice = st.checkbox("🎤 Use Live Voice Input", value=False)
        if use_voice:
            audio_data = st.audio_input("Speak your topic:")
            if audio_data is not None:
                with st.spinner("Transcribing..."):
                    st.session_state.research_topic = speech_to_text(audio_data.read())
                    st.success(f"Transcribed: {st.session_state.research_topic}")

        topic = st.text_input("Enter your research goal:", value=st.session_state.research_topic, placeholder="e.g. Future of Mars Colonization")

        # Examples
        st.caption("💡 **Quick Start Examples:**")
        examples = ["Impact of LLMs on modern education", "Latest breakthroughs in Fusion Energy 2025", "Sustainability of EV Battery recycling"]
        ex_cols = st.columns(3)
        for i, ex_text in enumerate(examples):
            with ex_cols[i]:
                if st.button(ex_text, key=f"ex_{i}", use_container_width=True):
                    st.session_state.research_topic = ex_text
                    st.rerun()

    with col2:
        st.header("🎯 Options")
        all_languages = get_supported_languages()
        supported_codes = ['en', 'hi', 'ar', 'es', 'fr']
        supported_display = {k: v for k, v in all_languages.items() if k in supported_codes}
        
        selected_language = st.selectbox("🌍 Language", options=list(supported_display.keys()), format_func=lambda x: supported_display[x])
        st.subheader("📤 Exports")
        export_pdf = st.checkbox("Generate PDF Report", value=True)
        export_audio = st.checkbox("Generate Voice Summary", value=True)

    st.divider()

    # --- EXECUTION LOGIC ---
    if st.button("🚀 Start Nuclear Research", type="primary"):
        if not topic:
            st.error("Please provide a topic first.")
        else:
            st.session_state.research_topic = topic
            try:
                with st.status("🤖 Agents are working...", expanded=True) as status:
                    st.write("🔄 Initializing Specialist Agents...")
                    st.write("📡 Connecting to Knowledge Base...")
                    
                    crew_engine = ResearchCrew(topic=topic, language=selected_language, show_logs=True)
                    results = crew_engine.run()
                    status.update(label="✅ All Agents Finished!", state="complete", expanded=False)

                if results and 'report_path' in results:
                    st.success("✅ Research Completed Successfully!")
                    with st.spinner("🎧 Generating Multilingual Audio & Reports..."):
                        multilingual_data = generate_multilingual_assets(results['report_path'])

                    tab1, tab2, tab3 = st.tabs(["📝 English Report", "📄 PDF Preview", "🌍 Multilingual Hub"])

                    with tab1:
                        if os.path.exists(results['report_path']):
                            with open(results['report_path'], 'r', encoding='utf-8') as f:
                                report_content = f.read()
                            st.markdown(report_content)
                            st.download_button("📥 Download Markdown", report_content, file_name=os.path.basename(results['report_path']))
                        else:
                            st.error("Report file missing.")

                    with tab2:
                        if export_pdf and os.path.exists(results['report_path']):
                            pdf_path = results['report_path'].replace(".md", ".pdf")
                            if not os.path.exists(pdf_path):
                                with st.spinner("Generating professional PDF..."):
                                    with open(results['report_path'], 'r', encoding='utf-8') as f:
                                        content_for_pdf = f.read()
                                    generate_pdf(content_for_pdf, pdf_path)
                            if os.path.exists(pdf_path):
                                display_pdf_preview(pdf_path)
                                with open(pdf_path, "rb") as f:
                                    st.download_button("📥 Download Full PDF Report", f, file_name=os.path.basename(pdf_path), mime="application/pdf")
                            else:
                                st.warning("PDF generation failed.")
                        else:
                            st.info("PDF generation disabled.")

                    with tab3:
                        if multilingual_data:
                            st.write("### 🌐 Select Language")
                            selected_lang_key = st.selectbox("Choose a language:", list(multilingual_data.keys()))
                            lang_data = multilingual_data.get(selected_lang_key)
                            if lang_data:
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    st.subheader("🎧 Audio Summary")
                                    if os.path.exists(lang_data['audio_path']):
                                        st.audio(lang_data['audio_path'])
                                        with open(lang_data['audio_path'], "rb") as audio_file:
                                            st.download_button("⬇️ Download Audio", audio_file, file_name=f"Audio_{selected_lang_key}.mp3", mime="audio/mp3")
                                    else:
                                        st.info("Audio skipped.")
                                with col2:
                                    st.subheader("📄 Translated Report")
                                    if os.path.exists(lang_data['report_path']):
                                        st.success(f"Translation ready.")
                                        with open(lang_data['report_path'], "rb") as report_file:
                                            st.download_button("⬇️ Download Report", report_file, file_name=f"Report_{selected_lang_key}.md", mime="text/markdown")
                                    else:
                                        st.warning("Translation unavailable.")
                                st.divider()
                                st.caption(f"Text Preview ({selected_lang_key}):")
                                st.text_area("", lang_data['text'], height=300)
                        else:
                            st.warning("Multilingual assets not available.")
                else:
                    st.error("Crew failed to produce a final report.")
            
            except Exception as e:
                st.error(f"❌ Execution Stopped: {str(e)}")

# --- OTHER PAGES ---
elif page == "📚 Research History":
    st.header("📚 Research History")
    history = get_all_research(limit=20)
    if not history: st.info("No research history found.")
    else:
        for record in history:
            with st.expander(f"🕒 {record.created_at.strftime('%Y-%m-%d %H:%M')} | {record.topic}"):
                st.write(f"**Status:** {record.status}")
                if record.report_path and os.path.exists(record.report_path):
                    st.info(f"File Path: {record.report_path}")
                    with open(record.report_path, 'r', encoding='utf-8') as f:
                        st.text_area("Preview", f.read()[:500] + "...", height=150)

elif page == "🎤 Voice Input":
    st.header("🎤 Voice Command Center")
    st.info("Speak your research topic here to auto-fill the search bar.")
    v_audio = st.audio_input("Record your request:")
    if v_audio:
        text = speech_to_text(v_audio.read())
        st.session_state.research_topic = text
        st.success(f"Recognized: {text}")
        if st.button("Use this topic"):
            st.rerun()

elif page == "⚙️ Settings":
    st.header("⚙️ Configuration Status")
    st.json({k: "✅ Active" if v else "❌ Missing" for k, v in critical_keys.items()})
    st.write("**Virtual Environment:** `venv311`")
    st.write("**Framework:** CrewAI 1.6.1 + LiteLLM Bridge")

st.divider()
st.markdown("<center>AutoResearch Crew Pro • 2025 Nuclear Architecture • Sequential Pipeline</center>", unsafe_allow_html=True)