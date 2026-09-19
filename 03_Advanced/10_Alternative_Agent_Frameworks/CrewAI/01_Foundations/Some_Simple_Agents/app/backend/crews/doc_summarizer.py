"""Document Summarizer crew.

Accepts a file path (uploaded or written from pasted text).
Uses FileReadTool for the summarizer agent and a manager agent for quality control.
Uses Process.hierarchical with manager_agent.
"""
import queue
import threading

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import FileReadTool
from dotenv import load_dotenv

from utils import capture_to_queue

load_dotenv()

llm = LLM(model="databricks/databricks-gpt-5-4")


def run_summarizer_crew(
    path_to_file: str,
    output_queue: queue.Queue,
) -> None:
    with capture_to_queue(output_queue):
        try:
            file_read_tool = FileReadTool()

            summarizer = Agent(
                llm=llm,
                role="Text Summarizer",
                goal=f"Summarize the text in the file '{path_to_file}' into a concise and coherent summary.",
                backstory="A highly skilled summarizer specialized in condensing long texts.",
                tools=[file_read_tool],
                verbose=True,
            )

            manager = Agent(
                llm=llm,
                role="Content Quality Manager",
                goal="Ensure that the summary provided is realistic, coherent, and meets quality standards.",
                backstory="An experienced manager skilled in evaluating text summaries.",
                verbose=True,
            )

            summarize_task = Task(
                name="Summarize Text Task",
                agent=summarizer,
                description=f"Read the file at '{path_to_file}' and generate a concise, coherent summary.",
                expected_output="A brief and coherent summary of the document.",
            )

            crew = Crew(
                agents=[summarizer],
                tasks=[summarize_task],
                process=Process.hierarchical,
                manager_agent=manager,
                verbose=True,
            )

            result = crew.kickoff(inputs={"path_to_file": path_to_file})
            output_queue.put("__DONE__")
            output_queue.put(result.raw)

        except Exception as exc:
            output_queue.put(f"ERROR: {exc}")
            output_queue.put("__DONE__")
            output_queue.put(f"Crew failed: {exc}")


def start_summarizer_crew(path_to_file: str) -> queue.Queue:
    q: queue.Queue = queue.Queue()
    threading.Thread(
        target=run_summarizer_crew,
        args=(path_to_file, q),
        daemon=True,
    ).start()
    return q
