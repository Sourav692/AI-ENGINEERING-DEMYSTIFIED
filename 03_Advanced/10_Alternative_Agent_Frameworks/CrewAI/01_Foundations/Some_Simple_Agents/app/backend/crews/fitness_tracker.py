import queue
import threading
from typing import List

from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

from utils import capture_to_queue

load_dotenv()

llm = LLM(model="databricks/databricks-gpt-5-4")


def run_fitness_crew(
    fitness_goal: str,
    nutrition_preference: str,
    historical_weight_data: List[str],
    output_queue: queue.Queue,
) -> None:
    with capture_to_queue(output_queue):
        try:
            fitness_tracker_agent = Agent(
                llm=llm,
                role="Fitness Tracker",
                backstory="An AI-powered fitness tracker that helps users set goals, track progress, and recommend personalized workout plans.",
                goal="Set fitness goals, track user progress, and provide personalized recommendations based on user preferences.",
                verbose=True,
            )

            recommendation_agent = Agent(
                llm=llm,
                role="Recommendation Agent",
                backstory="An AI agent that fetches personalized fitness and nutrition recommendations based on user goals.",
                goal="Search for fitness and nutrition information to provide recommendations that match the user's goals.",
                tools=[SerperDevTool()],
                verbose=True,
            )

            set_and_track_goals = Task(
                description=(
                    f"Set the user's fitness goal to '{fitness_goal}' and track their progress with a "
                    f"personalized plan. Take into account the last weight measurements: {historical_weight_data}."
                ),
                expected_output="A fitness plan and progress tracking setup.",
                agent=fitness_tracker_agent,
            )

            fetch_recommendations = Task(
                description=(
                    f"Fetch fitness recommendations for goal '{fitness_goal}' and "
                    f"nutrition preference '{nutrition_preference}'."
                ),
                expected_output="Personalized fitness and nutrition recommendations.",
                agent=recommendation_agent,
            )

            provide_workout_plan = Task(
                description="Provide a step-by-step workout plan to help the user achieve their fitness goal.",
                expected_output="A personalized workout plan.",
                agent=fitness_tracker_agent,
            )

            crew = Crew(
                agents=[fitness_tracker_agent, recommendation_agent],
                tasks=[set_and_track_goals, fetch_recommendations, provide_workout_plan],
                planning=True,
                verbose=True,
            )

            result = crew.kickoff()
            output_queue.put("__DONE__")
            output_queue.put(result.raw)

        except Exception as exc:
            output_queue.put(f"ERROR: {exc}")
            output_queue.put("__DONE__")
            output_queue.put(f"Crew failed: {exc}")


def start_fitness_crew(
    fitness_goal: str,
    nutrition_preference: str,
    historical_weight_data: List[str],
) -> queue.Queue:
    q: queue.Queue = queue.Queue()
    threading.Thread(
        target=run_fitness_crew,
        args=(fitness_goal, nutrition_preference, historical_weight_data, q),
        daemon=True,
    ).start()
    return q
