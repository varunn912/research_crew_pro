from crewai import Agent
from src.llm.multi_provider import get_summarizer_llm
import yaml

class SummarizerAgent:
    def get_agent(self):
        # Load config safely
        try:
            with open('config/agents.yaml', 'r') as f:
                config = yaml.safe_load(f)['summarizer_agent']
        except Exception:
            # Fallback config
            config = {
                'role': 'Executive Summarizer',
                'goal': 'Synthesize complex information into concise summaries for {topic}',
                'backstory': 'You are a communication expert. You distill complex research into clear executive points.'
            }

        # Use the specific Summarizer LLM (Qwen 2.5 is excellent for this)
        llm = get_summarizer_llm()

        return Agent(
            role=config['role'],
            goal=config['goal'], # Topic is formatted in the Task description usually, but kept for safety
            backstory=config['backstory'],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )