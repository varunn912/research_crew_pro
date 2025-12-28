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
        # 1. Initialize Agents
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

        # Task 2: Trend Analysis
        analysis_task = Task(
            description=f"Analyze the research data for '{self.topic}'. Identify emerging trends, patterns, and future predictions.",
            expected_output="A trend analysis report highlighting patterns and market shifts.",
            agent=analyst,
            context=[research_task]
        )

        # Task 3: Content Extraction
        extraction_task = Task(
            description=f"Extract relevant technical details and dense information related to '{self.topic}'.",
            expected_output="Structured extracted data and technical summaries.",
            agent=extractor,
            context=[research_task]
        )

        # Task 4: Summarization
        summary_task = Task(
            description=f"Summarize the analysis and extracted data into concise executive points in {self.language}.",
            expected_output="A set of concise executive summaries and bullet points.",
            agent=summarizer,
            context=[analysis_task, extraction_task]
        )

        # Task 5: Fact Checking (Now runs BEFORE writing)
        fact_check_task = Task(
            description=f"Verify the research findings, analysis, and summaries. Ensure statistics, facts, and logical consistency are accurate before the report is written.",
            expected_output="A verified and corrected set of data points and summaries, ready for writing.",
            agent=fact_checker,
            context=[research_task, analysis_task, summary_task]
        )

        # Task 6: Writing (Now the FINAL Step)
        write_task = Task(
            description=f"Write a comprehensive professional report on '{self.topic}' in {self.language}. Use the verified facts and analysis provided.",
            expected_output=f"A high-quality markdown research report in {self.language}.",
            agent=writer,
            context=[fact_check_task], # Depends on the Fact Checker's output
            output_file=f"output/{self.topic.replace(' ', '_')}_final.md"
        )

        # 3. Assemble the Crew (Order Updated)
        crew = Crew(
            agents=[researcher, analyst, extractor, summarizer, fact_checker, writer],
            tasks=[research_task, analysis_task, extraction_task, summary_task, fact_check_task, write_task],
            process=Process.sequential,
            verbose=True,
            output_log_file=self.output_log_file
        )

        # 4. Kickoff!
        result = crew.kickoff()
        
        return {
            "result": result, 
            "report_path": write_task.output_file # The Writer now produces the final file
        }