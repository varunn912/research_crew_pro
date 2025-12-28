import os
from crewai import Crew, Process, Task
from src.agents.research_agent import ResearchAgent
from src.agents.trend_analyst_agent import TrendAnalystAgent
from src.agents.content_extractor_agent import ContentExtractorAgent
from src.agents.summarizer_agent import SummarizerAgent
from src.agents.report_writer_agent import ReportWriterAgent
from src.agents.fact_checker_agent import FactCheckerAgent

class ResearchCrew:
    def __init__(self, topic, language='en'):
        self.topic = topic
        self.language = language
        self.output_log_file = "output/crew_execution.log"

    def run(self):
        # 1. Initialize Agents (They now auto-fetch their specific LLMs)
        researcher = ResearchAgent().get_agent()
        analyst = TrendAnalystAgent().get_agent()
        extractor = ContentExtractorAgent().get_agent()
        summarizer = SummarizerAgent().get_agent()
        writer = ReportWriterAgent().get_agent()
        fact_checker = FactCheckerAgent().get_agent()

        # 2. Define Tasks
        # Task 1: Research
        research_task = Task(
            description=f"Conduct extensive research on: '{self.topic}'. Find key facts, latest developments, and statistics.",
            expected_output="A comprehensive list of research findings, URLs, and raw data points.",
            agent=researcher
        )

        # Task 2: Trend Analysis (DeepSeek)
        analysis_task = Task(
            description=f"Analyze the research data for '{self.topic}'. Identify emerging trends, patterns, and future predictions.",
            expected_output="A trend analysis report highlighting patterns and market shifts.",
            agent=analyst,
            context=[research_task]
        )

        # Task 3: Content Extraction (Gemini)
        extraction_task = Task(
            description=f"Extract relevant technical details and dense information related to '{self.topic}'.",
            expected_output="Structured extracted data and technical summaries.",
            agent=extractor,
            context=[research_task]
        )

        # Task 4: Summarization (Qwen)
        summary_task = Task(
            description=f"Summarize the analysis and extracted data into concise executive points in {self.language}.",
            expected_output="A set of concise executive summaries and bullet points.",
            agent=summarizer,
            context=[analysis_task, extraction_task]
        )

        # Task 5: Writing (Qwen)
        write_task = Task(
            description=f"Write a comprehensive professional report on '{self.topic}' in {self.language}. Use the analysis and summaries provided.",
            expected_output=f"A high-quality markdown research report in {self.language}.",
            agent=writer,
            context=[summary_task, analysis_task]
        )

        # Task 6: Fact Checking (DeepSeek)
        fact_check_task = Task(
            description=f"Review the draft report. Verify statistics, facts, and logical consistency. Correct any hallucinations.",
            expected_output=f"A finalized, fact-checked, and polished research report in {self.language}.",
            agent=fact_checker,
            context=[write_task],
            output_file=f"output/{self.topic.replace(' ', '_')}_final.md"
        )

        # 3. Assemble the Crew
        crew = Crew(
            agents=[researcher, analyst, extractor, summarizer, writer, fact_checker],
            tasks=[research_task, analysis_task, extraction_task, summary_task, write_task, fact_check_task],
            process=Process.sequential,  # Agents work one after another
            verbose=True,
            output_log_file=self.output_log_file
        )

        # 4. Kickoff!
        result = crew.kickoff()
        
        # Return the final file path for the UI to display
        return {
            "result": result, 
            "report_path": fact_check_task.output_file
        }