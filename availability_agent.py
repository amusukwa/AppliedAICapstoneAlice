from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.tools import tool
import os
from typing import Literal
from datetime import datetime, timedelta

# Load environment variables (for API keys)
load_dotenv()

# Define system prompt for multilingual responses
system_prompt = """
You are a helpful bot, which only replies in Chichewa and English
For example,
Q: Muli bwanji?
A:
Chichewa: Ndili bwino, zikomo
English: I am fine, thank you

You help users check availability and find information.
"""

# Mock database of availability slots
availability_database = {
    "monday": ["09:00", "10:00", "14:00", "15:00", "16:00"],
    "tuesday": ["09:00", "11:00", "13:00", "15:00"],
    "wednesday": ["10:00", "11:00", "14:00", "16:00"],
    "thursday": ["09:00", "10:00", "13:00", "15:00"],
    "friday": ["09:00", "11:00", "14:00", "16:00"]
}

@tool
def check_availability(day: str, time_slot: str = None) -> str:
    """
    Check availability for a specific day and optionally a specific time slot.
    Args:
        day: The day to check (monday, tuesday, etc.)
        time_slot: Optional specific time to check (format: HH:MM)
    """
    day = day.lower()
    
    if day not in availability_database:
        return f"Sorry, we only have availability information for weekdays (Monday-Friday)."
    
    if time_slot:
        if time_slot in availability_database[day]:
            return f"The time slot {time_slot} is available on {day.capitalize()}!"
        else:
            return f"The time slot {time_slot} is not available on {day.capitalize()}. Available slots are: {', '.join(availability_database[day])}"
    
    return f"Available time slots for {day.capitalize()}: {', '.join(availability_database[day])}"

@tool
def book_appointment(day: str, time_slot: str) -> str:
    """
    Book an appointment for a specific day and time slot.
    Args:
        day: The day to book (monday, tuesday, etc.)
        time_slot: The time to book (format: HH:MM)
    """
    day = day.lower()
    
    if day not in availability_database:
        return f"Cannot book appointment. We only operate on weekdays (Monday-Friday)."
    
    if time_slot in availability_database[day]:
        availability_database[day].remove(time_slot)
        return f"Successfully booked appointment for {day.capitalize()} at {time_slot}!"
    else:
        return f"Cannot book appointment. Time slot {time_slot} is not available on {day.capitalize()}."

# Keep your existing search tool
@tool
def search(query: str):
    """Use this to search for information on any topic."""
    search_results = {
        "population": "According to recent data, New York City has approximately 8.8 million residents.",
        "landmarks": "Famous landmarks include the Statue of Liberty, Empire State Building, Central Park.",
        "food": "New York is known for its pizza, bagels, cheesecake, and diverse international cuisine.",
        "transport": "New York has an extensive subway system, buses, taxis, and three major airports."
    }
    
    for key, value in search_results.items():
        if key in query.lower():
            return value
    
    return f"Searched for '{query}'. [Mock search response]"

# Collect all tools
tools = [search, check_availability, book_appointment]

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
    print("Example 1: Availability Check")
    inputs = {"messages": [("user", "what times are available on Monday?")]}
    print_stream(graph.stream(inputs, stream_mode="values"))
    
    print(f"\n\n{'==='*20}\n\n")
    
    print("Example 2: Specific Time Slot Check")
    inputs = {"messages": [("user", "is 10:00 available on Tuesday?")]}
    print_stream(graph.stream(inputs, stream_mode="values"))
    
    print(f"\n\n{'==='*20}\n\n")
    
    print("Example 3: Book Appointment")
    inputs = {"messages": [("user", "book an appointment for Monday at 14:00")]}
    print_stream(graph.stream(inputs, stream_mode="values"))