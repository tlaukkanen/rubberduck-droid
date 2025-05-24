"""
Test script for the DroidAgent long-term memory functionality.
This script demonstrates how to use the memory features.
"""

import os
from dotenv import load_dotenv
from droid.agent.droid_agent import DroidAgent

# Load environment variables
load_dotenv()

def test_memory_functionality():
    """Test the long-term memory features of DroidAgent."""
    
    # Initialize the agent with a test user ID
    agent = DroidAgent(enable_voice=False, user_id="test_user_123")
    
    print("=== DroidAgent Memory Test ===\n")
    
    # Test storing some memories
    test_queries = [
        # Store some personal information
        "Remember that my favorite programming language is Python and I work as a software engineer at Microsoft.",
        
        # Store a preference
        "I prefer to work in the morning and I like my coffee black.",
        
        # Ask the agent to recall information
        "What do you remember about my job?",
        
        # Ask about preferences
        "What are my preferences for coffee and work schedule?",
        
        # Store technical information
        "I'm working on a Star Wars droid project using Azure Cosmos DB for persistence.",
        
        # Test retrieval of technical info
        "What technical projects am I working on?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        
        try:
            response = agent.answer_question_with_ssml(query)
            print(f"Response: {response}\n")
            print("-" * 50 + "\n")
        except Exception as e:
            print(f"Error: {e}\n")
    
    print("=== Memory Test Complete ===")

if __name__ == "__main__":
    # Check if required environment variables are set
    required_vars = ["COSMOS_ENDPOINT", "COSMOS_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file based on .env.example")
    else:
        test_memory_functionality()
