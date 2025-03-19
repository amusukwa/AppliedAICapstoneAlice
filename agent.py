# Import necessary libraries
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.tools import tool
import os
from typing import Literal

# Load environment variables (for API keys)
load_dotenv()

# Define system prompt for multilingual responses
system_prompt = """
You are a helpful bot, which only replies in  Chichewa and English
For example,
Q: Muli bwanji?
A:
Chichewa: Ndili bwino, zikomo
English: I am fine, thank you


You help users find information and check weather conditions.
"""

# Define the weather tool
@tool
def get_weather(city: Literal["nyc", "sf", "toronto", "london", "nairobi"]):
    """Use this to get weather information for specific cities."""
    weather_data = {
        "nyc": "It might be cloudy in NYC with temperatures around 65°F.",
        "sf": "It's sunny in San Francisco with temperatures around 70°F.",
        "toronto": "It's currently snowing in Toronto with temperatures around 28°F.",
        "london": "It's rainy in London with temperatures around 55°F.",
        "nairobi": "It's warm and partly cloudy in Nairobi with temperatures around 75°F."
    }
    
    if city.lower() in weather_data:
        return weather_data[city.lower()]
    else:
        return f"Weather data for {city} is not available. Available cities are: nyc, sf, toronto, london, and nairobi."

# Define the search tool
@tool
def search(query: str):
    """Use this to search for information on any topic."""
    # In a real implementation, this would connect to a search API
    # This is a simplified mock implementation
    search_results = {
        "population": "According to recent data, New York City has approximately 8.8 million residents, making it the most populous city in the United States.",
        "landmarks": "Famous landmarks include the Statue of Liberty, Empire State Building, Central Park, Times Square, and Brooklyn Bridge.",
        "food": "New York is known for its pizza, bagels, cheesecake, and diverse international cuisine from its many cultural neighborhoods.",
        "transport": "New York has an extensive subway system, buses, taxis, and is served by three major airports: JFK, LaGuardia, and Newark."
    }
    
    for key, value in search_results.items():
        if key in query.lower():
            return value
    
    return f"Searched for '{query}'. Here are some general facts about this topic. [This is a mock search response for demonstration purposes.]"

# Collect the tools
tools = [get_weather, search]

# Initialize the language model
model = ChatOpenAI(model="gpt-4o", temperature=0)

# Create the ReAct agent
graph = create_react_agent(model, tools=tools, prompt=system_prompt)

# Function to stream and print responses
def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

# Example usage
if __name__ == "__main__":
    print("Example 1: Weather Query")
    inputs = {"messages": [("user", "what is the weather in New York?")]}
    print_stream(graph.stream(inputs, stream_mode="values"))
    
    print(f"\n\n{'==='*20}\n\n")
    
    print("Example 2: Search Query")
    inputs = {"messages": [("user", "tell me about the population of New York")]}
    print_stream(graph.stream(inputs, stream_mode="values"))
    
    print(f"\n\n{'==='*20}\n\n")
    
    print("Example 3: Combined Query")
    inputs = {"messages": [("user", "compare the weather in nyc and nairobi, and tell me about famous landmarks in both cities")]}
    print_stream(graph.stream(inputs, stream_mode="values"))