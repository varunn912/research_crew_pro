import os
import yaml
from typing import List, Type
from pydantic import BaseModel, Field
from crewai import Agent
from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
from src.llm.multi_provider import get_researcher_llm

# --- INTERNAL TOOLS ---

class WebSearchInput(BaseModel):
    query: str = Field(..., description="The search query for Tavily.")

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web using Tavily AI for recent data and news."
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            response = client.search(query=query, search_depth="advanced", include_answer=True, max_results=5)
            results = []
            if response.get('answer'):
                results.append(f"--- TAVILY AI SUMMARY ---\n{response['answer']}\n")
            for idx, result in enumerate(response.get('results', []), 1):
                results.append(f"{idx}. {result.get('title')}\n   URL: {result.get('url')}")
            return "\n".join(results)
        except Exception as e:
            return f"Web search error: {str(e)}"

class DuckDuckGoTool(BaseTool):
    """
    A custom wrapper for LangChain's DuckDuckGoSearchRun to ensure 
    Pydantic V2 compatibility with CrewAI Agents.
    """
    name: str = "duckduckgo_search"
    description: str = "Search the web using DuckDuckGo for current events and information."

    def _run(self, query: str) -> str:
        try:
            ddg_search = DuckDuckGoSearchRun()
            return ddg_search.run(query)
        except Exception as e:
            return f"DuckDuckGo search error: {str(e)}"

# --- AGENT CREATION ---

def create_research_agent(topic: str, show_logs: bool = True) -> Agent:
    """
    Fixed Researcher Agent: Ensures all tools are valid BaseTool instances.
    """
    try:
        with open('config/agents.yaml', 'r') as f:
            config = yaml.safe_load(f)['research_agent']
    except:
        config = {'role': 'Senior Researcher', 'goal': f'Research {topic}', 'backstory': 'Expert investigator.'}

    # Initialize tools as CrewAI BaseTool instances to avoid Pydantic validation errors
    # Note: Using the custom wrappers we defined above
    search_tool_tavily = WebSearchTool()
    search_tool_ddg = DuckDuckGoTool()
    
    # Get the specific LLM instance for this agent
    llm = get_researcher_llm() 

    return Agent(
        role=config['role'],
        goal=config['goal'].format(topic=topic),
        backstory=config['backstory'],
        llm=llm,
        # PASSING TOOLS: All items in this list are now instances of BaseTool
        tools=[search_tool_tavily, search_tool_ddg], 
        verbose=show_logs,
        allow_delegation=False,
        memory=True
    )