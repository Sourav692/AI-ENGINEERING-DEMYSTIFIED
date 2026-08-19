from deepeval.test_case import LLMTestCase, ToolCall, ToolCallParams
from deepeval.metrics import ToolCorrectnessMetric
from dotenv import load_dotenv
load_dotenv()

available_tools = [
    ToolCall(name="FlightSearch",
             input_parameters={"origin": "str",
                               "destination": "str", "date": "str"},
             description="Search flights tool"),
    ToolCall(name="WeatherCheck",
             input_parameters={"city": "str", "date": "str"},
             description="Check weather for a city"),
    ToolCall(name="HotelSearch",
             input_parameters={"city": "str",
                               "check_in": "str", "check_out": "str"},
             description="Search hotels in a city"),
    ToolCall(name="CurrencyConvert",
             input_parameters={"from": "str", "to": "str", "amount": "float"},
             description="Convert from one currency to another"),
    ToolCall(name="WeatherCheckV2",
             input_parameters={"city": "str", "date": "str"},
             description="Newer weather tool"),
]

test_case = LLMTestCase(
    input="Find me flights from NYC to London on 2026-03-13 and check the weather there.",
    actual_output="Found 2 flights from NYC to London. Weather in London: 12°C, cloudy.",

    tools_called=[
        ToolCall(
            name="FlightSearch",
            input_parameters={"origin": "NYC", "destination": "London",
                              "date": "2026-03-13"},
            output={"flights":
                    [{"id": "BA178", "price_usd": 412}, {
                        "id": "VS4", "price_usd": 389}],
                    "total": 2}
        ),
        ToolCall(
            name="WeatherCheck",
            input_parameters={"city": "London", "date": "2026-03-13"},
        ),
    ],

    expected_tools=[
        ToolCall(
            name="FlightSearch",
            input_parameters={"origin": "NYC", "destination": "London",
                              "date": "2026-03-13"},
            output={"flights":
                    [{"id": "BA178", "price_usd": 412}, {
                        "id": "VS4", "price_usd": 389}],
                    "total": 2}
        ),
        ToolCall(
            name="WeatherCheck",
            input_parameters={"city": "London", "date": "2026-03-13"},
        ),
    ],
)

metric = ToolCorrectnessMetric(
    evaluation_params=[
        ToolCallParams.INPUT_PARAMETERS,
        ToolCallParams.OUTPUT,
    ],
    should_exact_match=True,
    # available_tools=available_tools,
    # model="openai/gpt-4o-2024-08-06",
    include_reason=True,
)

metric.measure(test_case)
print(f"Score: {metric.score}")
print(f"Reason: {metric.reason}")
