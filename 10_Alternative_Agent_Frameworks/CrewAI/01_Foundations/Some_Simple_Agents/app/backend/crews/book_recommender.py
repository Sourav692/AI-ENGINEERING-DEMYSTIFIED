import os
import queue
import threading

from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

from utils import capture_to_queue

load_dotenv()

MEM0_API_KEY = os.getenv("MEM0_API_KEY", "")

llm = LLM(model="databricks/databricks-gpt-5-4")


def run_book_crew(
    user_id: str,
    user_preferences: str,
    output_queue: queue.Queue,
) -> None:
    with capture_to_queue(output_queue):
        try:
            recommendation_agent = Agent(
                llm=llm,
                role="Book Recommendation Specialist",
                backstory="An AI-powered book advisor who suggests books based on user preferences and past interactions.",
                goal="Provide personalised book recommendations.",
                verbose=True,
            )

            suggest_task = Task(
                description=(
                    f"Suggest three personalised book recommendations based on "
                    f"user preferences: {user_preferences}."
                ),
                expected_output="A list of three book titles with a brief description of each.",
                agent=recommendation_agent,
            )

            memory_config: dict = {}
            if MEM0_API_KEY:
                memory_config = {
                    "provider": "mem0",
                    "config": {"user_id": user_id, "api_key": MEM0_API_KEY},
                }

            crew = Crew(
                agents=[recommendation_agent],
                tasks=[suggest_task],
                process=Process.sequential,
                memory=bool(MEM0_API_KEY),
                **({"memory_config": memory_config} if memory_config else {}),
                verbose=True,
            )

            result = crew.kickoff()

            # Also store the conversation in Mem0 for future context
            if MEM0_API_KEY:
                try:
                    from mem0 import MemoryClient
                    client = MemoryClient(api_key=MEM0_API_KEY)
                    client.add(
                        [
                            {"role": "user", "content": f"Recommendation for: {user_preferences}"},
                            {"role": "assistant", "content": result.raw},
                        ],
                        user_id=user_id,
                    )
                    print("Memory stored in Mem0.")
                except Exception as mem_exc:
                    print(f"Mem0 storage warning: {mem_exc}")

            output_queue.put("__DONE__")
            output_queue.put(result.raw)

        except Exception as exc:
            output_queue.put(f"ERROR: {exc}")
            output_queue.put("__DONE__")
            output_queue.put(f"Crew failed: {exc}")


def start_book_crew(user_id: str, user_preferences: str) -> queue.Queue:
    q: queue.Queue = queue.Queue()
    threading.Thread(
        target=run_book_crew,
        args=(user_id, user_preferences, q),
        daemon=True,
    ).start()
    return q
