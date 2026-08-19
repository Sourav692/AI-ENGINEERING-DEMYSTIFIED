from deepeval.metrics import ArgumentCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

TOOL_SCHEMAS = {
    "FlightSearch": {
        "required_keys": {"origin", "destination", "date"},
        "validators": {
            "date": (lambda v: datetime.strptime(v, "%Y-%m-%d"), "YYYY-MM-DD")
        }
    }
}


def validate_args(tools_called: list[ToolCall]) -> tuple[bool, str]:
    for tool in tools_called:
        schema = TOOL_SCHEMAS.get(tool.name)
        if not schema:
            continue

        actual_keys = set(tool.input_parameters.keys())
        required_keys = schema["required_keys"]

        missing = required_keys - actual_keys
        if missing:
            return False, f"{tool.name}: missing required args {missing}"

        extra = actual_keys - required_keys
        if extra:
            return False, f"{tool.name}: unexpected args {extra}"

        for field, (validator, fmt) in schema["validators"].items():
            value = tool.input_parameters.get(field)
            try:
                validator(value)
            except (ValueError, TypeError):
                return False, f"{tool.name}: '{field}' must be '{fmt}', got '{value}'"

    return True, "ok"


metric = ArgumentCorrectnessMetric(
    threshold=0.7,
    model="openai/gpt-4o-2024-08-06",
    include_reason=True,
)

test_case = LLMTestCase(
    input="Find me flights from New York to Paris on March 15, 2026",
    actual_output="I found 3 flights from NYC to Paris on March 15.",
    tools_called=[
        ToolCall(
            name="FlightSearch",
            description="Search for available flights between cities on a given date (date in YYYY-MM-DD format).",
            input_parameters={"origin": "NYC",
                              "destination": "Paris", "date": "2026-03-15"}
        ),
    ],
)

valid, reason = validate_args(test_case.tools_called)
if not valid:
    print(f"Score: 0\nReason: {reason}")
else:
    metric.measure(test_case)
    print(f"Score: {metric.score}\nReason: {metric.reason}")
