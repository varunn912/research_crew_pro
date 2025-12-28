import yaml
import os
from crewai import Agent
from src.llm.multi_provider import get_gemini_llm

def create_report_writer_agent(topic: str, show_logs: bool = True) -> Agent:
    """
    Final agent in the hierarchy. Compiles verified research into a 
    polished report and can trigger multimodal outputs.
    """
    try:
        with open('config/agents.yaml', 'r') as f:
            config = yaml.safe_load(f)['report_writer_agent']
    except (FileNotFoundError, KeyError):
        config = {
            'role': 'Senior Technical Content Strategist',
            'goal': f'Assemble verified findings into a professional report on {topic}.',
            'backstory': 'You are a master of clarity, turning complex data into engaging narratives.'
        }

    # Gemini 3 Flash for massive context (1M tokens) and multimodal support
    llm = get_gemini_llm(temperature=0.7)

    return Agent(
        role=config['role'],
        goal=config['goal'].format(topic=topic),
        backstory=config['backstory'] + (
            "\n\nYou specialize in Markdown formatting. Your reports must include "
            "an Executive Summary, a Table of Contents, and deep technical sections."
        ),
        llm=llm,
        tools=[],  # Usually works with internal context, but can add Google Docs/Notion tools here
        verbose=show_logs,
        allow_delegation=False,
        memory=True,
        multimodal=True # Enables Dec 2025 multimodal processing
    )