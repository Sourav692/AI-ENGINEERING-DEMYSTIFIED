from deepeval.metrics import ToolUseMetric
from deepeval.test_case import Turn, ConversationalTestCase, ToolCall
from dotenv import load_dotenv
load_dotenv()

convo_test_case = ConversationalTestCase(
    turns=[
        Turn(role="user", content="Find me a hotel in Paris for March 15-18, 2026"),
        Turn(
            role="assistant",
            content="I found one option. The Hotel Le Marais (id: 'le-marais-paris') has availability at $180/night.",
            tools_called=[
                ToolCall(
                    name="HotelSearch",
                    input_parameters={
                        "city": "Paris", "checkin": "2026-03-15", "checkout": "2026-03-18"},
                    output={"hotel_id": "le-marais-paris",
                            "name": "Le Marais", "price_usd": 180}
                )
            ]
        ),
        Turn(role="user", content="Yes, book the same please (id: 'le-marais-paris'), from 15 to 18 March."),
        Turn(
            role="assistant",
            content="Done! Your reservation is confirmed. Confirmation: HTL-9921.",
            tools_called=[
                ToolCall(
                    name="HotelBooking",
                    input_parameters={"hotel_id": "le-marais-paris",
                                      "checkin": "2026-03-15", "checkout": "2026-03-18"},
                    output={"confirmation": "HTL-9921"}
                )
            ]
        ),
    ],
)

metric = ToolUseMetric(
    model="openai/gpt-4o-2024-08-06",
    include_reason=True,
    available_tools=[
        ToolCall(name="HotelSearch",
                 description="Search for hotels by city and dates"),
        ToolCall(name="HotelBooking",
                 description="Book a hotel by hotel ID and dates"),
        ToolCall(name="FlightSearch",
                 description="Search for flights between cities"),
        ToolCall(name="CarRental", description="Search for rental cars"),
    ],
    # strict_mode=True,
)

metric.measure(convo_test_case)
print(f"Score: {metric.score}")
print(f"Reason: {metric.reason}")
