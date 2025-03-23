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

You help users find information.
"""

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
tools = [search]

# Initialize the language model
model = ChatOpenAI(model="gpt-4", temperature=0)

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
    print("Example 1: Search Query")
    inputs = {"messages": [("user", "tell me about the population of New York")]}
    print_stream(graph.stream(inputs, stream_mode="values"))
    
    print(f"\n\n{'==='*20}\n\n")
    
    print("Example 2: Landmarks Query")
    inputs = {"messages": [("user", "what are some famous landmarks in New York?")]}
    print_stream(graph.stream(inputs, stream_mode="values"))