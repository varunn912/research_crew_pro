import os
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai import Agent
from crewai.tools import BaseTool
from src.llm.multi_provider import get_ollama_llm
from bs4 import BeautifulSoup # Standard in CrewAI environments

class TavilyContentInput(BaseModel):
    url: str = Field(..., description="The URL of the webpage to read")

class TavilyContentTool(BaseTool):
    name: str = "read_webpage_content"
    description: str = "Reads the full text content from a single URL. Uses API with manual fallback."
    args_schema: Type[BaseModel] = TavilyContentInput

    def _run(self, url: str) -> str:
        # 1. Attempt Tavily API (Primary)
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
            
            # Try the modern 'extract' method first
            if hasattr(client, 'extract'):
                response = client.extract(urls=[url])
                if response and 'results' in response:
                    return response['results'][0].get('raw_content', "")
            
            # Fallback to 'search' (Legacy Tavily versions)
            # We use the URL as the query, which often returns the page context
            response = client.search(query=url, include_raw_content=True, max_results=1)
            if response and 'results' in response and len(response['results']) > 0:
                return response['results'][0].get('content', "")

        except Exception as e:
            print(f"⚠️ Tavily API extraction failed: {e}. Switching to manual fallback...")

        # 2. Attempt Manual Scrape (Bulletproof Fallback)
        # This runs if Tavily fails or doesn't have the method.
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Parse text with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles for clean text
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
                
            text = soup.get_text(separator=' ', strip=True)
            
            # Return first 15k chars to avoid overwhelming the LLM
            return text[:15000] if text else "No text content found on page."

        except Exception as e:
            return f"Error: Could not extract content from {url}. Reason: {str(e)}"

def create_content_extractor_agent(topic: str, show_logs: bool = True) -> Agent:
    # Using Ollama (Local) for efficient reading
    llm = get_ollama_llm(temperature=0.1) 
    
    return Agent(
        role="Content Extractor",
        goal=f"Extract clean, technical data about {topic} from raw URLs.",
        backstory=(
            "You are a data parsing specialist. Your expertise lies in reading long academic or technical "
            "articles and extracting only the relevant specs, figures, and technical truths. "
            "You ignore advertising and navigation noise."
        ),
        llm=llm,
        tools=[TavilyContentTool()],
        verbose=show_logs,
        allow_delegation=False,
        max_iter=5 # Limit retries to keep it fast
    )