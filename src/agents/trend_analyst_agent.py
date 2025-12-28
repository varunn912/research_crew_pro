import os
import matplotlib.pyplot as plt
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
from crewai import Agent
from crewai.tools import BaseTool
from src.llm.multi_provider import get_analyst_llm

# Fix for Matplotlib backend on headless servers (like Streamlit Cloud)
plt.switch_backend('Agg')

# --- 1. VISUALIZATION TOOL (Preserved & Robust) ---

class VisualizationInput(BaseModel):
    data: Dict[str, Any] = Field(..., description="Data dictionary containing 'labels' (list) and 'values' (list).")
    title: str = Field(..., description="The title of the chart.")
    chart_type: str = Field(default="bar", description="The type of chart to generate: 'bar', 'line', or 'pie'.")
    output_filename: str = Field(..., description="Filename for the image, e.g., 'market_trends.png'.")

class VisualizationTool(BaseTool):
    name: str = "create_visualization"
    description: str = "Generates and saves a chart (bar/line) to visualize data trends."
    args_schema: Type[BaseModel] = VisualizationInput

    def _run(self, data: Dict, title: str, chart_type: str, output_filename: str) -> str:
        try:
            # Ensure output directory exists
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            save_path = os.path.join(output_dir, output_filename)
            
            plt.figure(figsize=(10, 6))
            
            if chart_type == "bar":
                plt.bar(data['labels'], data['values'], color='steelblue')
            elif chart_type == "line":
                plt.plot(data['labels'], data['values'], marker='o', linestyle='-', color='darkorange')
            
            plt.title(title)
            plt.xlabel("Categories")
            plt.ylabel("Values")
            plt.tight_layout()
            
            plt.savefig(save_path)
            plt.close() # Close figure to free memory
            
            return f"Chart successfully saved to {save_path}"
        except Exception as e:
            return f"Error creating visualization: {str(e)}"

# --- 2. AGENT CLASS (The Fix) ---

class TrendAnalystAgent:
    def get_agent(self):
        # Initialize the Visualization Tool
        viz_tool = VisualizationTool()

        # Connect to the Analyst LLM (DeepSeek/Qwen via Router)
        llm = get_analyst_llm()

        return Agent(
            role='Market Trend Analyst',
            goal='Analyze scattered data points to identify emerging patterns, market shifts, and future predictions regarding {topic}.',
            backstory="""You are an expert data strategist and futurist. You do not just read data; 
            you see the story behind it. You excel at connecting unrelated dots to predict 
            where a technology or market trend is heading. You visualize your findings whenever possible.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            tools=[viz_tool] # Agent can now make charts!
        )