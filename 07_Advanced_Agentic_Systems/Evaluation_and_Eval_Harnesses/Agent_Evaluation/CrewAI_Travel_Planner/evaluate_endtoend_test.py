from deepeval import evaluate
import pytest
import pandas as pd
import requests
import os
from deepeval.metrics import TaskCompletionMetric
from deepeval.test_case import LLMTestCase
from dotenv import load_dotenv, find_dotenv


from deepeval.test_case import ToolCall

# Load API Key
load_dotenv(find_dotenv())
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Constants
EXCEL_FILE = "./trip_questions.xlsx"  # update this
BACKEND_URL = "http://localhost:8000/plan_trip"  # your FastAPI endpoint

# Metric
task_completion = TaskCompletionMetric(threshold=0.7)

# Load the Excel file
test_data = pd.read_excel(EXCEL_FILE)

@pytest.mark.parametrize("row", test_data.iterrows())
def test_trip_planner_with_deepeval(row):
    index, data = row

    # Read test input
    origin = data["origin"]
    city = data["city"]
    interest = data["interest"]
    date_range = data["date_range"]

    # Call the Trip API
    payload = {
        "origin": origin,
        "city": city,
        "customer_interest_topic": interest,
        "date_range": date_range
    }

    response = requests.post(BACKEND_URL, json=payload)
    assert response.status_code == 200, f"API call failed: {response.text}"

    result = response.json()["trip_plan"]
    print("****************************")
    print(result)

    task_description = (
        f"Create a 7-day trip plan from {origin} to {city}, focused on {interest} "
        f"for the date range {date_range}. "
        f"The output should include: top 3 places for the interest, 5 city attractions, "
        f"a day-by-day itinerary with packing and budget tips."
    )

    # Construct test case
    test_case = LLMTestCase(
        input=task_description,
        actual_output=result,
        expected_output="The plan should include detailed travel suggestions including points of interest and budget tips.",
        tools_called=[
                ToolCall(
                    name="search internet",
                    description="Searches the internet for travel-related queries like city attractions, interests, and plans.",
                    input_parameters={"query": task_description},
                    output=result
                ),
                ToolCall(
                    name="calculate",
                    description="Performs budget calculations for trip planning",
                    input_parameters={"operation": "2000 * 2 + 1500"},
                    output="5500"
                )
                ],
            )

    task_completion.measure(test_case)

    # Debugging & Excel writing
    print(f"Score: {task_completion.score}")
    print(f"Reason: {task_completion.reason}")

    test_data.at[index, "score"] = task_completion.score
    test_data.at[index, "reason"] = task_completion.reason

    # Score check
    assert 0 <= task_completion.score <= 1, f"Score out of range: {task_completion.score}"

    evaluate(test_cases=[test_case], metrics=[task_completion])



# Save updated Excel file after test
def teardown_module(module):
    test_data.to_excel(EXCEL_FILE, index=False)
