import os

from crewai.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper


class SearchTools():

  @staticmethod
  @tool("Search the internet")
  def search_internet(query: str):
    """ Useful to search the internet about a given topic and return relevant results.
    
    Expected input: { "query": "<your search text>" }"""
    # Option 1: Using environment variable
    serper_api_key = os.environ.get("SERPER_API_KEY")

    # Option 2: Passing directly (if not using env var)
    # serper_api_key = "your_api_key_here"

    search_engine = GoogleSerperAPIWrapper(serper_api_key=serper_api_key) # Or GoogleSerperAPIWrapper() if using env var
    results = search_engine.run(query)
    return results