from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_google_community import GoogleSearchAPIWrapper
from googletrans import Translator
import os

# Load environment variables (for API keys)
load_dotenv()

# Initialize Google Search
search = GoogleSearchAPIWrapper(
    google_api_key=os.getenv("GOOGLE_API_KEY"),  # Correct usage: os.getenv
    google_cse_id=os.getenv("GOOGLE_CSE_ID")
)

translator = Translator()

# Define system prompt for multilingual responses
system_prompt = """
You are a helpful bot, which only replies in Chichewa, English and French.
You can also translate user queries and responses to and from Chichewa, English, and French.
For example,
Q: Muli bwanji?
A:
Chichewa: Ndili bwino, zikomo
English: I am fine, thank you

You help users find information about trending books and their availability.
You can search for books by:
- Current trends
- Specific titles
- Genre
- General availability

"""


@tool
def search_trending_books(query: str):
    """Search for information about trending books based on the given query."""
    search_query = f"trending books {query}"
    results = search.run(search_query)
    
    if results:
        return f"Here are some trending books related to your search:\n{results}"
    return "No trending books found matching your search criteria."

@tool
def check_book_availability(book_title: str):
    """Check the availability of a specific book."""
    search_query = f"{book_title} book availability purchase"
    results = search.run(search_query)

    if results:
        return f"Here's availability information for {book_title}:\n{results}"
    return "Could not find availability information for this book."

@tool
def get_all_available_books():
    """Get a list of all currently available trending books."""
    search_query = "current bestselling books trending now"
    results = search.run(search_query)

    if results:
        return f"Here are the current trending books:\n{results}"
    return "Could not fetch trending books at the moment."

@tool
def search_books_by_genre(genre: str):
    """Search for trending books in a specific genre."""
    search_query = f"best selling {genre} books current trending"
    results = search.run(search_query)

    if results:
        return f"Here are popular books in the {genre} genre:\n{results}"
    return f"No trending books found in the {genre} genre."

# Collect all tools
tools = [
    search_trending_books,
    check_book_availability,
    get_all_available_books,
    search_books_by_genre
]

# Initialize the language model
model = ChatOpenAI(model="gpt-4", temperature=0)

# Create the ReAct agent
graph = create_react_agent(model, tools=tools, prompt=system_prompt)

# Function to handle language translation
def translate_text(text, target_lang):
    return translator.translate(text, dest=target_lang).text

# Function to stream and print responses
def print_stream(stream, target_lang='en'):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            translated_message = translate_text(message[1], target_lang)
            print((message[0], translated_message))
        else:
            translated_message = translate_text(message.content, target_lang)
            print(translated_message)

# Example usage demonstrating multilingual support
if __name__ == "__main__":
    # Set target language (e.g., 'en' for English, 'es' for Spanish, 'fr' for French, 'ny' for Chichewa)
    target_language = 'es'  # Example: Setting the target language to Spanish

    print("Example 1: Search Trending Books")
    inputs = {"messages": [("user", "what trending books are available?")]}
    print_stream(graph.stream(inputs, stream_mode="values"), target_language)

    print(f"\n\n{'==='*20}\n\n")

    print("Example 2: Check Specific Book Availability")
    inputs = {"messages": [("user", "is Tomorrow and Tomorrow available?")]}
    print_stream(graph.stream(inputs, stream_mode="values"), target_language)