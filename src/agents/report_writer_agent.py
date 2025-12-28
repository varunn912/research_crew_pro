import yaml
from crewai import Agent
from src.llm.multi_provider import get_writer_llm

class ReportWriterAgent:
    def get_agent(self):
        try:
            with open('config/agents.yaml', 'r') as f:
                config = yaml.safe_load(f)['report_writer_agent']
        except (FileNotFoundError, KeyError):
            config = {
                'role': 'Senior Technical Content Strategist',
                'goal': 'Assemble verified findings into a professional report.',
                'backstory': 'You are a master of clarity, turning complex data into engaging narratives.'
            }

        # Use Qwen (via Writer LLM router) for better human-like prose
        llm = get_writer_llm()

        return Agent(
            role=config['role'],
            goal=config['goal'],
            backstory=config['backstory'] + (
                "\n\nYou specialize in Markdown formatting. Your reports must include "
                "an Executive Summary, a Table of Contents, and deep technical sections."
            ),
            llm=llm,
            tools=[], # Can access context from previous agents
            verbose=True,
            allow_delegation=False,
            memory=True
        )