from crewai import Agent
from src.llm.multi_provider import get_gemini_llm
import yaml
from typing import List

# --- CORRECTED FUNCTION SIGNATURE ---
def create_summarizer_agent(topic: str, show_logs: bool = True, tools: List = []) -> Agent:
    
    with open('config/agents.yaml', 'r') as f:
        config = yaml.safe_load(f)['summarizer_agent']
    
    llm = get_gemini_llm(temperature=0.7)
    
    return Agent(
        role=config['role'],
        goal=config['goal'].format(topic=topic),
        backstory=config['backstory'],
        llm=llm,
        tools=tools,
        verbose=show_logs, # <-- USE THE PASSED VALUE
        allow_delegation=False
    )