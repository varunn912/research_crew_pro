import os
import yaml
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
from crewai import Agent
from crewai.tools import BaseTool
from src.llm.multi_provider import get_gemini_llm

plt.switch_backend('Agg')

class VisualizationInput(BaseModel):
    data: Dict[str, Any] = Field(..., description="Data dict with 'labels' and 'values'")
    title: str = Field(..., description="Chart title")
    chart_type: str = Field(default="bar", description="bar, line, or pie")
    output_filename: str = Field(..., description="e.g., 'trends.png'")

class VisualizationTool(BaseTool):
    name: str = "create_visualization"
    description: str = "Create charts to visualize trends and data."
    args_schema: Type[BaseModel] = VisualizationInput

    def _run(self, data: Dict, title: str, chart_type: str, output_filename: str) -> str:
        try:
            os.makedirs('outputs', exist_ok=True)
            save_path = os.path.join('outputs', output_filename)
            plt.figure(figsize=(10, 6))
            if chart_type == "bar":
                plt.bar(data['labels'], data['values'], color='steelblue')
            elif chart_type == "line":
                plt.plot(data['labels'], data['values'], marker='o')
            plt.title(title)
            plt.savefig(save_path)
            plt.close()
            return f"Chart saved to {save_path}"
        except Exception as e:
            return f"Plotting error: {str(e)}"

def create_trend_analyst_agent(topic: str, show_logs: bool = True) -> Agent:
    with open('config/agents.yaml', 'r') as f:
        config = yaml.safe_load(f)['trend_analyst_agent']
    
    # Gemini for high-reasoning synthesis
    llm = get_gemini_llm(temperature=0.7)
    
    return Agent(
        role=config['role'],
        goal=config['goal'].format(topic=topic),
        backstory=config['backstory'],
        llm=llm,
        tools=[VisualizationTool()],
        verbose=show_logs,
        allow_delegation=False
    )