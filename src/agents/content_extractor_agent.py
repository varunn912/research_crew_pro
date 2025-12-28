import os
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai import Agent
from crewai.tools import BaseTool
from src.llm.multi_provider import get_extractor_llm
from bs4 import BeautifulSoup 

# --- TOOL DEFINITION ---
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
            api_key = os.getenv("TAVILY_API_KEY")
            if api_key:
                client = TavilyClient(api_key=api_key)
                
                # Try 'extract' method
                if hasattr(client, 'extract'):
                    response = client.extract(urls=[url])
                    if response and 'results' in response:
                        return response['results'][0].get('raw_content', "")
                
                # Fallback to 'search'
                response = client.search(query=url, include_raw_content=True, max_results=1)
                if response and 'results' in response and len(response['results']) > 0:
                    return response['results'][0].get('content', "")

        except Exception as e:
            print(f"⚠️ Tavily API extraction failed: {e}. Switching to manual fallback...")

        # 2. Attempt Manual Scrape (Bulletproof Fallback)
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
                
            text = soup.get_text(separator=' ', strip=True)
            
            # Return first 20k chars (Gemini can handle this easily)
            return text[:20000] if text else "No text content found on page."

        except Exception as e:
            return f"Error: Could not extract content from {url}. Reason: {str(e)}"

# --- AGENT CLASS ---
class ContentExtractorAgent:
    def get_agent(self):
        # Use Gemini (Extractor LLM) for massive context window reading
        llm = get_extractor_llm()
        
        return Agent(
            role="Content Extractor",
            goal="Extract clean, technical data about {topic} from raw URLs.",
            backstory=(
                "You are a data parsing specialist. Your expertise lies in reading long academic or technical "
                "articles and extracting only the relevant specs, figures, and technical truths. "
                "You ignore advertising and navigation noise."
            ),
            llm=llm,
            tools=[TavilyContentTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=5 
        )