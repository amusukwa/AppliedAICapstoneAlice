from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSearchAPIWrapper
import os
from typing import Literal
from datetime import datetime

# Load environment variables (for API keys)
load_dotenv()

# Initialize Google Search
search = GoogleSearchAPIWrapper(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    google_cse_id=os.getenv("GOOGLE_CSE_ID")
)

# Define system prompt for multilingual responses
system_prompt = """
You are a helpful bot, which only replies in Chichewa and English
For example,
Q: Muli bwanji?
A:
Chichewa: Ndili bwino, zikomo
English: I am fine, thank you

You help users find information about trending books and their availability.
"""

@tool
def search_trending_books(query: str):
    """Search for information about trending books."""
    search_query = f"trending books {query}"
    results = search.run(search_query)
    
    if results:
        return f"Here are some trending books related to your search:\n{results}"
    return "No trending books found matching your search criteria."

@tool
def check_book_availability(book_title: str):
    """Check availability of a specific book."""
    search_query = f"{book_title} book availability purchase"
    results = search.run(search_query)
    
    if results:
        return f"Here's availability information for {book_title}:\n{results}"
    return "Could not find availability information for this book."

@tool
def get_all_available_books():
    """Get a list of current trending books."""
    search_query = "current bestselling books trending now"
    results = search.run(search_query)
    
    if results:
        return f"Here are the current trending books:\n{results}"
    return "Could not fetch trending books at the moment."

# Collect all tools
tools = [search_trending_books, check_book_availability, get_all_available_books]

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
    print("Example 1: Search Trending Books")
    inputs = {"messages": [("user", "what trending books are available?")]}
    print_stream(graph.stream(inputs, stream_mode="values"))
    
    print(f"\n\n{'==='*20}\n\n")
    
    print("Example 2: Check Specific Book Availability")
    inputs = {"messages": [("user", "is Tomorrow and Tomorrow available?")]}
    print_stream(graph.stream(inputs, stream_mode="values"))
    
    print(f"\n\n{'==='*20}\n\n")
    
    print("Example 3: Search by Author")
    inputs = {"messages": [("user", "show me books by Rebecca Yarros")]}
    print_stream(graph.stream(inputs, stream_mode="values"))