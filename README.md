# 🤖 AutoResearch Crew — Multi-Agent AI Research Assistant

> **An advanced, production-ready multi-agent research automation system with multilingual, export, and AI orchestration capabilities.**

---

## 📘 Table of Contents

* [Overview](#-overview)
* [Key Features](#-key-features)
* [Architecture](#-architecture)
* [Installation](#-installation)
* [Usage](#-usage)
* [Technologies](#-technologies)
* [System Requirements](#-system-requirements)
* [Project Structure](#-project-structure)
* [Future Enhancements](#-future-enhancements)
* [Contributing & Support](#-contributing--support)

---

## 🎯 Overview

**AutoResearch Crew** is a next-generation, multi-agent AI system built with the **CrewAI** framework and powered by **Groq**, **Gemini**, and **OpenAI** models. It automates complex research workflows — from data collection and summarization to report writing and multilingual export.

### 🚨 Problem

Manual research is time-intensive, error-prone, and often lacks multi-perspective insights.

### ✅ Solution

AutoResearch Crew enables:

* Automated multi-agent collaboration
* Real-time fact-checking and analysis
* Multilingual processing (15+ languages)
* Smart exports (Google Docs, Notion, PDF)
* Advanced analytics and voice input

### 🎯 Target Users

* 🧑‍🔬 Researchers & Academics
* 🧑‍💼 Business Analysts
* ✍️ Content Creators
* 🎓 Students
* 🧠 Professionals

---

## ✨ Key Features

### 🤖 Multi-Agent AI System

| Agent               | Role                 | Responsibility                                     |
| ------------------- | -------------------- | -------------------------------------------------- |
| 🕵️ Research Agent  | Information Gatherer | Web search, data collection, source identification |
| ✍️ Summarizer Agent | Content Curator      | Information synthesis and theme extraction         |
| ✅ Fact Checker      | Quality Assurance    | Accuracy verification and bias detection           |
| 📈 Trend Analyst    | Data Scientist       | Pattern recognition and statistical analysis       |
| 📄 Report Writer    | Document Specialist  | Generates structured reports with citations        |

---

### 🔄 Multi-Provider LLM System

| Priority | Provider      | Model              | Purpose                         |
| -------- | ------------- | ------------------ | ------------------------------- |
| 1️⃣      | Groq          | `llama-3.3-70b`    | High-speed, free-tier inference |
| 2️⃣      | Google Gemini | `gemini-1.5-flash` | Reliable fallback provider      |
| 3️⃣      | OpenAI        | `gpt-4o-mini`      | High-quality reasoning          |

**Benefits**

* ⚡ Automatic failover
* 💰 Cost optimization
* 📊 Intelligent routing
* 🚀 Zero downtime

---

### 🌍 Multi-Language Support

* 15+ supported languages
* Real-time translation using `deep-translator`
* RTL language handling (Arabic, Hebrew)
* Multilingual PDF & audio (TTS) output

---

### 📤 Advanced Export Options

* **Google Docs:** OAuth 2.0 one-click export
* **Notion:** Automatic database & block creation
* **PDF:** UTF-8 compliant, professional formatting

---

### 🎧 Audio Integration (TTS / STT)

* **Text-to-Speech:** Multilingual MP3 summaries via Google TTS
* **Speech-to-Text:** Voice-based topic input using Google Speech API

---

### 📊 Analytics & History

* SQLite persistence layer
* Research execution metrics
* Searchable history dashboard

---

## 🏗️ Architecture

```
User Interface (Streamlit / CLI / API)
        ↓
Application Orchestrator (CrewAI)
        ↓
Research → Summarize → Fact Check → Analyze → Write
        ↓
Export Layer (PDF / Docs / Notion / Audio)
```

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/autoresearch-crew.git
cd autoresearch-crew
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
pip install langchain-groq google-generativeai langchain-google-genai
```

### 4️⃣ Configure API Keys

Create `.env` based on `.env.example`:

```env
GROQ_API_KEY=
GEMINI_API_KEY=
OPENAI_API_KEY=
TAVILY_API_KEY=
NOTION_API_KEY=
NOTION_DATABASE_ID=
```

---

## 🚀 Usage

### 🖥️ Web Interface

```bash
streamlit run app.py
```

### 💻 CLI Usage

```bash
python run.py "AI in Healthcare" --pdf --audio --language es
```

### 🧠 Programmatic Usage

```python
from src.crew import ResearchCrew

crew = ResearchCrew(
    topic="Impact of AI on education",
    language="en",
    enable_audio=True,
    export_google_docs=True
)
results = crew.run()
```

---

## 🧩 Technologies

| Category    | Technology                  |
| ----------- | --------------------------- |
| Framework   | CrewAI                      |
| LLM Routing | LangChain                   |
| UI          | Streamlit                   |
| Database    | SQLite + SQLAlchemy         |
| Translation | deep-translator             |
| Audio       | gTTS, SpeechRecognition     |
| Export      | Google Docs API, Notion API |

---

## 🖥️ System Requirements

| Requirement | Minimum                  | Recommended   |
| ----------- | ------------------------ | ------------- |
| Python      | 3.10                     | 3.11          |
| RAM         | 4 GB                     | 8+ GB         |
| OS          | Windows 10 / macOS 10.14 | Ubuntu 22.04+ |

---

## 📁 Project Structure

```bash
autoresearch-crew/
├── app.py
├── run.py
├── requirements.txt
├── src/
│   ├── agents/
│   ├── crew/
│   ├── llm/
│   ├── translation/
│   ├── export/
│   ├── audio/
│   ├── database/
│   └── utils/
├── outputs/
└── data/
```

---

## 🚧 Future Enhancements

* 🌐 REST API for automation
* 🧠 Domain-specific fine-tuning
* 📊 Interactive visualizations
* 🗣️ Voice-driven research
* ☁️ Cloud synchronization

---

## 🤝 Contributing & Support

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a Pull Request 🚀

📫 **Support:** [support@autoresearch.ai](mailto:support@autoresearch.ai)

---

🧠 *AutoResearch Crew — redefining AI-powered research through multi-agent collaboration.*
