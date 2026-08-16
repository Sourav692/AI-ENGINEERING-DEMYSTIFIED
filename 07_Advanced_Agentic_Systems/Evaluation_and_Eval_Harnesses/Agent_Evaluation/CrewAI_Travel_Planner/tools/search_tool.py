import json
import os

import requests
from crewai.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper


class SearchTools():

  @staticmethod
  @tool("Search the internet")
  def search_internet1(query: dict):
    """ Useful to search the internet about a given topic and return relevant results.
    
    Expected input: { "query": "<your search text>" }"""
    """ query = input.get("query", "")
    if not query:
        return "No query provided." """

    #print("******* QUERY*******", query)
    top_result_to_return = 3
    url = "https://google.serper.dev/search"
    #payload = json.dumps({"q": query})
    payload = json.dumps(query)
    headers = {
        'X-API-KEY':'afce7db6435d58024290963b565ac78eb87d7105f38408457ebc9bf67adb5d4a',
        'content-type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # check if there is an organic key
    if 'organic' not in response.json():
      return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
    else:
      results = response.json()['organic']
      string = []
      for result in results[:1]:
        try:
          string.append('\n'.join([
              f"Title: {result['title']}", f"Link: {result['link']}",
              f"Snippet: {result['snippet']}", "\n-----------------"
          ]))
        except KeyError:
          next
      #print('\n'.join(string))  
      return '\n'.join(string)
    
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