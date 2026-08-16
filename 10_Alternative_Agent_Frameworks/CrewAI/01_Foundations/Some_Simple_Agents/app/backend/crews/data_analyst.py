"""Data Analyst crew.

Accepts a CSV path (uploaded to uploads/) and a user instruction.
Processes data with CodeInterpreterTool and saves result to outputs/<uuid>.csv.
SSE emits [DOWNLOAD] /outputs/<uuid>.csv at the end.
"""
import queue
import threading
import uuid
from pathlib import Path

from crewai import Agent, Task, Crew, LLM
from crewai_tools import CodeInterpreterTool
from dotenv import load_dotenv

from utils import capture_to_queue

load_dotenv()

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

llm = LLM(model="databricks/databricks-gpt-5-4")


def run_data_analyst_crew(
    dataframe_path: str,
    user_instruction: str,
    output_queue: queue.Queue,
) -> None:
    output_filename = f"{uuid.uuid4()}.csv"
    output_path = str(OUTPUTS_DIR / output_filename)
    download_path = f"/outputs/{output_filename}"

    with capture_to_queue(output_queue):
        try:
            data_analyst_agent = Agent(
                llm=llm,
                role="General Data Analyst",
                goal="Perform data analysis tasks based on user instructions and execute them using Python.",
                backstory="An experienced data analyst skilled in Python and data manipulation.",
                max_retry_limit=3,
                tools=[CodeInterpreterTool()],
                verbose=True,
            )

            task = Task(
                description=(
                    f"Load the dataframe from '{dataframe_path}', perform the following task: "
                    f"'{user_instruction}', and save the resulting dataframe to '{output_path}'. "
                    f"Execute the task using Python. If you cannot execute the code, explain why."
                ),
                expected_output=f"Dataframe with the applied operations saved to '{output_path}'.",
                agent=data_analyst_agent,
            )

            crew = Crew(
                agents=[data_analyst_agent],
                tasks=[task],
                verbose=True,
            )

            result = crew.kickoff()

            output_queue.put(f"[DOWNLOAD] {download_path}")
            output_queue.put("__DONE__")
            output_queue.put(result.raw)

        except Exception as exc:
            output_queue.put(f"ERROR: {exc}")
            output_queue.put("__DONE__")
            output_queue.put(f"Crew failed: {exc}")


def start_data_analyst_crew(
    dataframe_path: str, user_instruction: str
) -> queue.Queue:
    q: queue.Queue = queue.Queue()
    threading.Thread(
        target=run_data_analyst_crew,
        args=(dataframe_path, user_instruction, q),
        daemon=True,
    ).start()
    return q
