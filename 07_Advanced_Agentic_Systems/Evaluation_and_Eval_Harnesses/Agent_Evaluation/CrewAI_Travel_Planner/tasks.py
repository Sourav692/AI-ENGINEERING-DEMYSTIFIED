from crewai import Task
from textwrap import dedent

class TripTasks:
    def customer_interest_search_tasks(self, agent, city, customer_interest_topic):
        return Task(
            description=dedent(f"Search query: 'Best places to fulfill {customer_interest_topic} in {city}'"),
            agent=agent,
            expected_output="Top 3 places to fulfill customer interest"
        )

    def trip_info(self, agent, city, date_range):
        return Task(
            description=dedent(f"Identify 5 tourist attractions in {city} during {date_range}"),
            agent=agent,
            expected_output="Comprehensive city guide"
        )

    def plan_task(self, agent, origin, city, date_range):
        return Task(
            description=dedent(f"Create a 7-day travel plan with packing suggestions and budget from {origin} to {city} for {date_range}"),
            agent=agent,
            expected_output="Complete travel itinerary"
        )