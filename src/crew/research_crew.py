import os
import time
import requests
from crewai import Agent, Crew, Process, Task
from src.llm.multi_provider import (
    get_planner_llm, 
    get_researcher_llm, 
    get_fact_checker_llm, 
    get_extractor_llm
)
from crewai_tools import SerperDevTool
from src.agents.content_extractor_agent import TavilyContentTool 

class ResearchCrew:
    def __init__(self, topic: str, language: str = 'en', show_logs: bool = True):
        self.topic = topic
        self.language = language
        self.show_logs = show_logs
        self.timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.report_path = f"output/report_{self.timestamp}.md"

    def run(self):
        # --- 1. DEFINE AGENTS ---
        
        # We use Groq for the high-level reasoning
        groq_brain = get_planner_llm()

        planner = Agent(
            role="Strategic Planner",
            goal=f"Plan the research for {self.topic}",
            backstory="You are a strategic thinker.",
            llm=groq_brain,
            verbose=self.show_logs
        )

        researcher = Agent(
            role="Senior Data Discovery Specialist",
            goal=f"Find EXACTLY 3 high-quality URLs for {self.topic}",
            backstory="Expert at finding info.",
            llm=get_researcher_llm(),
            tools=[SerperDevTool()],
            verbose=self.show_logs
        )

        extractor = Agent(
            role="Content Extractor",
            goal="Extract key facts from the provided URLs.",
            backstory="Efficient reading machine.",
            llm=get_extractor_llm(),
            tools=[TavilyContentTool()],
            verbose=self.show_logs,
            max_iter=3
        )

        fact_checker = Agent(
            role="Chief Fact Verification Officer",
            goal="Verify extracted data.",
            backstory="Skeptical fact checker.",
            llm=get_fact_checker_llm(),
            verbose=self.show_logs
        )

        # ❌ WRITER AGENT REMOVED (We will write manually to avoid errors)

        # --- 2. DEFINE TASKS ---
        plan_task = Task(
            description=f"Plan research for: {self.topic}",
            expected_output="Search queries list.",
            agent=planner
        )

        search_task = Task(
            description=f"Find 3 relevant URLs for {self.topic}.",
            expected_output="List of 3 URLs.",
            agent=researcher,
            context=[plan_task]
        )

        extract_task = Task(
            description="Read the 3 URLs and extract key facts.",
            expected_output="Summarized facts.",
            agent=extractor,
            context=[search_task]
        )

        verify_task = Task(
            description="Verify data and output a clean list of facts.",
            expected_output="Verified facts.",
            agent=fact_checker,
            context=[extract_task]
        )

        # --- 3. RUN CREW ---
        crew = Crew(
            agents=[planner, researcher, extractor, fact_checker],
            tasks=[plan_task, search_task, extract_task, verify_task],
            process=Process.sequential,
            verbose=True,
            # 🔥 CRITICAL FIX: Disable internal planning to stop "Task Execution Planner" crash
            planning=False, 
            # Force manager to Groq just in case
            manager_llm=groq_brain 
        )

        print("🚀 Starting Research Phase...")
        research_result = crew.kickoff()
        print("✅ Research Phase Complete.")

        # --- 4. DIRECT WRITE PHASE (Bypassing Agents) ---
        print("✍️  Starting Direct Write Phase...")
        
        try:
            # We explicitly ask Groq to write the report via HTTP
            final_text = self._write_report_directly(str(research_result))
            print("✅ Report Written Successfully via Direct Link.")
        except Exception as e:
            print(f"❌ Direct Write Failed: {e}")
            final_text = f"# Research Facts (Writing Failed)\n\n{research_result}"

        # --- 5. SAVE & RETURN (Triggers PDF/Audio in App.py) ---
        os.makedirs('output', exist_ok=True)
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(str(final_text))
            
        return {'report_path': self.report_path}

    def _write_report_directly(self, context_data):
        """
        Directly hits the Groq API to write the report.
        Bypasses all CrewAI/LiteLLM routing logic.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key: return "Error: No GROQ_API_KEY found."

        url = "https://api.groq.com/openai/v1/chat/completions"
        
        prompt = f"""
        You are a professional technical writer.
        Write a detailed report in {self.language}.
        
        SOURCE MATERIAL:
        {context_data}
        
        INSTRUCTIONS:
        1. Write a clear Title.
        2. Use Headers (##) for sections.
        3. Use bullet points.
        4. Write at least 500 words.
        5. Output ONLY the report markdown.
        """

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a helpful report writer."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error generating report: {response.text}"