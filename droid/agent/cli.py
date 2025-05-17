import sys
import os
from droid.agent import DroidAgent

def main():
    # Load .env file from project root if present
    try:
        from dotenv import load_dotenv
        # Find project root (assume this file is always two levels below root)
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        dotenv_path = os.path.join(root_dir, '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
    except ImportError:
        pass  # If python-dotenv is not installed, skip silently

    print("Welcome to DroidAgent CLI! Type 'exit' to quit.")
    agent = DroidAgent()
    while True:
        try:
            print("")
            question = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break
        if question.strip().lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        response = agent.answer_question_with_ssml(question)
        print(f"DroidAgent: {response.strip()}")

if __name__ == "__main__":
    main()
