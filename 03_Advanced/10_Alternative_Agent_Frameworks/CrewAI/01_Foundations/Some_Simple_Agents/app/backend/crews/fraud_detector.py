"""Fraud Detection crew.

Uses ConditionalTask: escalation only triggers when > 5 anomalies are detected.
Uses manager_agent (hierarchical process).
"""
import queue
import threading
from typing import List

from crewai import Agent, Task, Crew, LLM
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
from pydantic import BaseModel
from dotenv import load_dotenv

from utils import capture_to_queue

load_dotenv()

llm = LLM(model="databricks/databricks-gpt-5-4")


class FraudDetectionOutput(BaseModel):
    anomalies: List[str]


def _is_escalation_needed(output: TaskOutput) -> bool:
    try:
        return len(output.pydantic.anomalies) > 5
    except Exception:
        return False


def run_fraud_crew(
    transaction_list: List[str],
    output_queue: queue.Queue,
) -> None:
    with capture_to_queue(output_queue):
        try:
            fraud_analyst = Agent(
                llm=llm,
                role="Fraud Analyst",
                goal="Analyze transactions to detect anomalies.",
                backstory="Experienced in financial fraud detection.",
                verbose=True,
            )

            escalation_specialist = Agent(
                llm=llm,
                role="Escalation Specialist",
                goal="Manually review and validate flagged transactions.",
                backstory="Handles complex fraud cases requiring detailed oversight.",
                verbose=True,
            )

            report_generator = Agent(
                llm=llm,
                role="Report Generator",
                goal="Prepare a summary fraud detection report.",
                backstory="Compiles findings into actionable insights.",
                verbose=True,
            )

            manager_agent = Agent(
                llm=llm,
                role="Fraud Detection Manager",
                goal="Oversee the fraud detection workflow and ensure efficient analysis.",
                backstory="Ensures efficient fraud analysis and resolution.",
                verbose=True,
            )

            task1 = Task(
                description=f"Analyze the following transactions for anomalies:\n{chr(10).join(transaction_list)}",
                agent=fraud_analyst,
                expected_output="List of anomalies detected for each transaction.",
                output_pydantic=FraudDetectionOutput,
            )

            conditional_task = ConditionalTask(
                description="Escalate flagged transactions if more than 5 anomalies are detected.",
                agent=escalation_specialist,
                condition=_is_escalation_needed,
                expected_output="Validated flagged transactions after manual review.",
            )

            report_task = Task(
                description="Generate a comprehensive summary report on the fraud detection results.",
                agent=report_generator,
                expected_output="A detailed fraud detection report with recommendations.",
            )

            crew = Crew(
                agents=[fraud_analyst, escalation_specialist, report_generator],
                tasks=[task1, conditional_task, report_task],
                manager_agent=manager_agent,
                planning=True,
                planning_llm=llm,
                verbose=True,
            )

            result = crew.kickoff()
            output_queue.put("__DONE__")
            output_queue.put(result.raw)

        except Exception as exc:
            output_queue.put(f"ERROR: {exc}")
            output_queue.put("__DONE__")
            output_queue.put(f"Crew failed: {exc}")


def start_fraud_crew(transaction_list: List[str]) -> queue.Queue:
    q: queue.Queue = queue.Queue()
    threading.Thread(
        target=run_fraud_crew,
        args=(transaction_list, q),
        daemon=True,
    ).start()
    return q
