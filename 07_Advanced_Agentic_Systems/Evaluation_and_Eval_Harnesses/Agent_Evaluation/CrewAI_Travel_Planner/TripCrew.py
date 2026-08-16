import os
from crewai import Agent
from tools.search_tool import SearchTools
from tools.calculator_tool import CalculatorTools
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

class TripAgents():
    def customer_interest_search_agent(self):
        return Agent(
            role='Customer_Interest_Search_Expert',
            goal='Get list of places of customer interested topic in the city',
            backstory='You will find out places of custoner interested topic',
            tools=[SearchTools.search_internet],
            verbose=True,
            llm=llm,
            max_iter=2
        )

    def local_expert(self):
        return Agent(
            role='Local Expert at this city',
            goal='Provide the BEST insights about the selected city',
            backstory='A knowledgeable local guide with extensive information about the city',
            tools=[SearchTools.search_internet],
            verbose=True,
            llm=llm,
            max_iter=2
        )

    def travel_concierge(self):
        return Agent(
            role='Amazing Travel Concierge',
            goal='Create the most amazing travel itineraries with budget and packing suggestions',
            backstory='Specialist in travel planning and logistics',
            tools=[SearchTools.search_internet, CalculatorTools.calculate],
            verbose=True,
            llm=llm,
            max_iter=2
        )

from crewai import Crew
from tasks import TripTasks

class TripCrew:
    def __init__(self, origin, city, customer_interest_topic, date_range):
        self.city = city
        self.origin = origin
        self.customer_interest_topic = customer_interest_topic
        self.date_range = date_range

    def run(self):
        agents = TripAgents()
        tasks = TripTasks()
        customer_agent = agents.customer_interest_search_agent()
        local_agent = agents.local_expert()
        concierge_agent = agents.travel_concierge()

        customer_task = tasks.customer_interest_search_tasks(customer_agent, self.city, self.customer_interest_topic)
        trip_info_task = tasks.trip_info(local_agent, self.city, self.date_range)
        plan_task = tasks.plan_task(concierge_agent, self.origin, self.city, self.date_range)

        crew = Crew(agents=[customer_agent, local_agent, concierge_agent], tasks=[customer_task, trip_info_task, plan_task], verbose=True)
        result = crew.kickoff()
        return result