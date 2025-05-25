#!/usr/bin/env python3

import traceback
import sys
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
print("Loading environment variables...")
load_dotenv()

# Check if necessary API keys are set
print(f"OPENAI_API_KEY set: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}")
print(f"SERPAPI_API_KEY set: {'Yes' if os.environ.get('SERPAPI_API_KEY') else 'No'}")

# If OPENAI_API_KEY is not set but AZURE keys are, use those instead
if not os.environ.get('OPENAI_API_KEY') and os.environ.get('AZURE_OPENAI_API_KEY'):
    print("Setting OPENAI_API_KEY from AZURE_OPENAI_API_KEY...")
    os.environ['OPENAI_API_KEY'] = os.environ['AZURE_OPENAI_API_KEY']

try:
    print("Importing LLM class...")
    from droid.brains import DroidAgent
    
    print("Creating LLM instance...")
    gpt = DroidAgent()
    print("LLM instance created successfully!")
    
    for tool in gpt.tools:
        print(f"Tool loaded: {tool.name} - {tool.description}")
    
    # Try a simple query to test the agent
    print("\nTesting agent with a simple query...")
    question = "What day of the week is today?"
    print(f"Question: {question}")
    
    print("Sending request to LangChain agent...")
    start_time = time.time()
    response = gpt.answer_question_with_ssml(question)
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f} seconds")
    print(f"Agent response: {response}")
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("Test completed successfully!")
