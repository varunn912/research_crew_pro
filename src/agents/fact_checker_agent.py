import os
import yaml
from typing import Type
from pydantic import BaseModel, Field
from crewai import Agent
from crewai.tools import BaseTool
from crewai_tools import SerperDevTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from src.llm.multi_provider import get_fact_checker_llm

# --- CUSTOM TOOL WRAPPER ---
class WikipediaToolInput(BaseModel):
    """Input schema for Wikipedia search."""
    query: str = Field(..., description="The search query to look up on Wikipedia.")

class WikipediaTool(BaseTool):
    name: str = "wikipedia_search"
    description: str = "Search Wikipedia for factual verification and background information."
    args_schema: Type[BaseModel] = WikipediaToolInput

    def _run(self, query: str) -> str:
        api_wrapper = WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=4000)
        wiki = WikipediaQueryRun(api_wrapper=api_wrapper)
        return wiki.run(query)

# --- AGENT CREATION ---
def create_fact_checker_agent(topic: str, show_logs: bool = True) -> Agent:
    try:
        with open('config/agents.yaml', 'r') as f:
            config = yaml.safe_load(f)['fact_checker_agent']
    except:
        config = {
            'role': 'Fact Verification Expert',
            'goal': f'Verify accuracy on {topic}',
            'backstory': 'Meticulous investigator ensuring 0% misinformation.'
        }

    # Initialize tools as BaseTool instances
    serper_tool = SerperDevTool()
    wiki_tool = WikipediaTool() # Using our wrapper
    
    llm = get_fact_checker_llm()

    return Agent(
        role=config['role'],
        goal=config['goal'].format(topic=topic),
        backstory=config['backstory'],
        llm=llm,
        tools=[serper_tool, wiki_tool], # Both are now valid BaseTool instances
        verbose=show_logs,
        allow_delegation=False
    )