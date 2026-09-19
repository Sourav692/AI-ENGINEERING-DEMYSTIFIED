"""Travel Advisor crew uses CrewAI Flows.

Since Flow does not support step_callback, we capture stdout/stderr
into the queue during flow.kickoff().
"""
import queue
import threading
from typing import List

from crewai import Agent, Task, Crew, LLM
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel
from dotenv import load_dotenv

from utils import capture_to_queue

load_dotenv()

llm = LLM(model="databricks/databricks-gpt-5-4")


# ---------------------------------------------------------------------------
# Agents (module-level so Flow methods can reference them)
# ---------------------------------------------------------------------------

def _make_agents():
    planner = Agent(
        llm=llm,
        role="Travel Planner",
        backstory="An expert in planning group vacations, considering budgets, destinations, and activities.",
        goal="Create a vacation plan based on traveler names, departure city, and destination.",
        verbose=True,
    )
    validator = Agent(
        llm=llm,
        role="Travel Plan Validator",
        backstory="An experienced travel advisor who ensures all plans meet safety, budget, and feasibility constraints.",
        goal="Evaluate vacation plans and validate if they meet predefined constraints.",
        verbose=True,
    )
    return planner, validator


# ---------------------------------------------------------------------------
# Flow definition
# ---------------------------------------------------------------------------

class TravelState(BaseModel):
    vacation_plan: str = ""
    is_plan_valid: bool = False
    generation_attempts_left: int = 2


class TravelAdvisorFlow(Flow[TravelState]):
    def __init__(self, names: List[str], city: str, destination: str):
        super().__init__()
        self.names = names
        self.city = city
        self.destination = destination
        self._planner, self._validator = _make_agents()

    @start()
    def generate_vacation_plan(self):
        print("Generating vacation plan...")
        task = Task(
            description=(
                f"Create a detailed vacation plan for travelers: {', '.join(self.names)}, "
                f"departing from {self.city} to {self.destination}. Include activities, "
                f"accommodation, and estimated costs."
            ),
            expected_output="A detailed vacation plan including activities, accommodation, and costs.",
            agent=self._planner,
        )
        crew = Crew(agents=[self._planner], tasks=[task], verbose=True)
        result = crew.kickoff()
        self.state.vacation_plan = result.raw
        print("Vacation plan generated.")

    @listen(generate_vacation_plan)
    def validate_vacation_plan(self):
        print("Validating vacation plan...")
        task = Task(
            description=(
                f"Evaluate this vacation plan: {self.state.vacation_plan}. "
                f"Ensure it is budget-friendly, includes at least two activities, and has "
                f"clear accommodation details. Reply with 'Valid' or 'Invalid'."
            ),
            expected_output="Valid or Invalid.",
            agent=self._validator,
        )
        crew = Crew(agents=[self._validator], tasks=[task], verbose=True)
        result = crew.kickoff()
        self.state.is_plan_valid = "Valid" in result.raw
        print("Validation:", "Valid" if self.state.is_plan_valid else "Invalid")

    @router(validate_vacation_plan)
    def route_vacation_plan(self):
        if self.state.is_plan_valid:
            return "valid"
        elif self.state.generation_attempts_left == 0:
            return "not_feasible"
        else:
            return "regenerate"

    @listen("valid")
    def finalize_vacation_plan(self):
        print("Plan is valid. Finalizing.")

    @listen("regenerate")
    def regenerate_vacation_plan(self):
        self.state.generation_attempts_left -= 1
        print(f"Regenerating plan... (attempts left: {self.state.generation_attempts_left})")
        self.generate_vacation_plan()

    @listen("not_feasible")
    def notify_user(self):
        print("Could not generate a feasible plan after multiple attempts.")


# ---------------------------------------------------------------------------
# Thread entry-point
# ---------------------------------------------------------------------------

def run_travel_crew(
    names: List[str],
    city: str,
    destination: str,
    output_queue: queue.Queue,
) -> None:
    with capture_to_queue(output_queue):
        try:
            import nest_asyncio
            nest_asyncio.apply()

            flow = TravelAdvisorFlow(names=names, city=city, destination=destination)
            flow.kickoff()

            output_queue.put("__DONE__")
            output_queue.put(flow.state.vacation_plan or "No feasible plan generated.")

        except Exception as exc:
            output_queue.put(f"ERROR: {exc}")
            output_queue.put("__DONE__")
            output_queue.put(f"Crew failed: {exc}")


def start_travel_crew(
    names: List[str], city: str, destination: str
) -> queue.Queue:
    q: queue.Queue = queue.Queue()
    threading.Thread(
        target=run_travel_crew,
        args=(names, city, destination, q),
        daemon=True,
    ).start()
    return q
