import yaml
import os
from crewai import Agent
from src.llm.multi_provider import get_gemini_llm
from src.export.google_docs import GoogleDocsTool
from src.export.notion import NotionTool


class ReportWriterAgent:
    def get_agent(self, topic: str, show_logs: bool = True) -> Agent:
        """
        Final agent in the hierarchy. Compiles verified research into a 
        polished report and can trigger optional export tools.
        """

        # --- 1. CONFIG LOGIC ---
        try:
            with open('config/agents.yaml', 'r') as f:
                config = yaml.safe_load(f)['report_writer_agent']
        except (FileNotFoundError, KeyError):
            config = {
                'role': 'Senior Technical Content Strategist',
                'goal': f'Assemble verified findings into a professional report on {topic}.',
                'backstory': 'You are a master of clarity, turning complex data into engaging narratives.'
            }

        # --- 2. OPTIONAL TOOL INITIALIZATION ---
        export_tools = []

        # Google Docs
        try:
            if os.getenv("GOOGLE_DOCS_TOKEN") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                export_tools.append(GoogleDocsTool())
        except Exception:
            pass

        # Notion
        try:
            if os.getenv("NOTION_TOKEN") or os.getenv("CREWAI_PLATFORM_INTEGRATION_TOKEN"):
                export_tools.append(NotionTool())
        except Exception:
            pass

        # --- 3. AGENT DEFINITION ---
        llm = get_gemini_llm(temperature=0.7)

        return Agent(
            role=config['role'],
            goal=config['goal'].format(topic=topic),
            backstory=config['backstory'] + (
                "\n\nYou specialize in Markdown formatting. Your reports must include "
                "an Executive Summary, a Table of Contents, and deep technical sections. "
                "If export tools are available, use them to save the final report."
            ),
            llm=llm,
            tools=export_tools,
            verbose=show_logs,
            allow_delegation=False,
            memory=True,
            multimodal=True
        )


# ✅ FIX: Add factory function expected by your project
def create_report_writer_agent(topic: str, show_logs: bool = True) -> Agent:
    return ReportWriterAgent().get_agent(topic, show_logs)