"""Employee Onboarding crew.

Uses kickoff_async(). We run asyncio.run() inside a daemon thread so the
event loop is isolated from FastAPI's event loop.
"""
import asyncio
import queue
import re
import threading
from typing import List, Type

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import BaseTool
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from utils import capture_to_queue

load_dotenv()

llm = LLM(model="databricks/databricks-gpt-5-4")


# ---------------------------------------------------------------------------
# Email Generator custom tool
# ---------------------------------------------------------------------------

class EmailGeneratorInput(BaseModel):
    fullname: str = Field(..., description="The full name of the employee.")
    department: str = Field(..., description="The department of the employee.")


class EmailGeneratorTool(BaseTool):
    name: str = "Email Generator"
    description: str = "Generates a company email based on the employee's full name and department."
    args_schema: Type[BaseModel] = EmailGeneratorInput

    def _run(self, fullname: str, department: str) -> str:
        name_part = re.sub(r"[^a-zA-Z.]", "", fullname.replace(" ", ".")).lower()
        dept_part = re.sub(r"[^a-zA-Z]", "", department).lower()
        return f"{name_part}@{dept_part}.company.com"


# ---------------------------------------------------------------------------
# Thread entry-point
# ---------------------------------------------------------------------------

def run_onboarding_crew(
    employees: List[dict],
    output_queue: queue.Queue,
) -> None:
    """Run onboarding crew synchronously inside its own asyncio event loop."""
    # Format employees list into the string representation the tasks expect
    employe_list = [
        f"{e['name']}, starting {e['start_date']}, department {e['department']}"
        for e in employees
    ]

    with capture_to_queue(output_queue):
        try:
            scheduler_agent = Agent(
                llm=llm,
                role="Scheduler",
                goal="Validate and confirm employee start dates.",
                backstory="Ensures the selected start date is a valid working day.",
                verbose=True,
            )

            it_agent = Agent(
                llm=llm,
                role="IT Administrator",
                goal="Set up company email accounts and provide PC setup instructions.",
                backstory="Prepares company email accounts and delivers simple PC setup guidelines.",
                tools=[EmailGeneratorTool()],
                verbose=True,
            )

            report_agent = Agent(
                llm=llm,
                role="Onboarding Reporter",
                goal="Generate a comprehensive onboarding summary report.",
                backstory="Creates a final onboarding report with all key details for HR records.",
                verbose=True,
            )

            validate_task = Task(
                description=(
                    "Check if the start dates for the following employees are working days. "
                    "If any date falls on a holiday or weekend, suggest the next available working day.\n"
                    f"Employees: {employe_list}"
                ),
                expected_output="Confirmed valid start dates or suggestions for each employee.",
                agent=scheduler_agent,
            )

            it_task = Task(
                description=(
                    "Create company emails for the following employees and provide PC setup instructions.\n"
                    f"Employees: {employe_list}"
                ),
                expected_output="Active company email addresses and clear PC setup instructions for each employee.",
                agent=it_agent,
            )

            report_task = Task(
                description=(
                    "Generate a comprehensive onboarding summary report for all employees including "
                    "email details, PC setup info, and start date confirmation.\n"
                    f"Employees: {employe_list}"
                ),
                expected_output="A clear and concise onboarding summary report for all employees.",
                agent=report_agent,
            )

            crew = Crew(
                agents=[scheduler_agent, it_agent, report_agent],
                tasks=[validate_task, it_task, report_task],
                process=Process.sequential,
                verbose=True,
            )

            # Run async kickoff in its own event loop
            result = asyncio.run(
                crew.kickoff_async(inputs={"employe": employe_list})
            )

            output_queue.put("__DONE__")
            output_queue.put(result.raw)

        except Exception as exc:
            output_queue.put(f"ERROR: {exc}")
            output_queue.put("__DONE__")
            output_queue.put(f"Crew failed: {exc}")


def start_onboarding_crew(employees: List[dict]) -> queue.Queue:
    q: queue.Queue = queue.Queue()
    threading.Thread(
        target=run_onboarding_crew,
        args=(employees, q),
        daemon=True,
    ).start()
    return q
