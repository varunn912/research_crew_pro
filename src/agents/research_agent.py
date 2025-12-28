import os
from typing import Type
from pydantic import BaseModel, Field
from crewai import Agent
from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
from src.llm.multi_provider import get_researcher_llm

# --- 1. DEFINE TOOLS (Preserved Custom Logic) ---

class WebSearchInput(BaseModel):
    query: str = Field(..., description="The search query for Tavily.")

class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web using Tavily AI for recent data and news."
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:
        try:
            from tavily import TavilyClient
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                return "Error: TAVILY_API_KEY is missing."
                
            client = TavilyClient(api_key=api_key)
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
    name: str = "duckduckgo_search"
    description: str = "Search the web using DuckDuckGo for current events and information."

    def _run(self, query: str) -> str:
        try:
            ddg_search = DuckDuckGoSearchRun()
            return ddg_search.run(query)
        except Exception as e:
            return f"DuckDuckGo search error: {str(e)}"

# --- 2. AGENT CLASS ---

class ResearchAgent:
    def get_agent(self):
        # Initialize the tools
        search_tool_tavily = WebSearchTool()
        search_tool_ddg = DuckDuckGoTool()

        # Connect to the correct LLM (DeepSeek/Qwen via Router)
        llm = get_researcher_llm()

        return Agent(
            role='Senior Research Analyst',
            goal='Uncover cutting-edge developments, verified facts, and comprehensive data on the given topic.',
            backstory="""You are an elite research analyst with a keen eye for detail. 
            You specialize in digging deep into complex topics to find the most relevant, 
            accurate, and up-to-date information available. You ignore superficial summaries 
            and look for raw data and primary sources.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[search_tool_tavily, search_tool_ddg]
        )