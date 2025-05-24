"""DroidAgent class for answering questions with SSML formatting and web search capabilities."""
# droid/agent/droid_agent.py

import os
import time
from typing import List, Tuple
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel, Field
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.chat_message_histories import ChatMessageHistory
from .long_term_memory import create_memory_tool


class DroidAgent:
    """
    A class that represents a humorous Star Wars droid agent capable of answering questions
    using SSML formatting. The agent can also perform web searches if a valid API key is provided.
    """
    
    def __init__(self, enable_voice: bool = True, user_id: str = "default_user"):
        self.last_question_time = time.time()
        self.user_id = user_id
        
        # Initialize tools
        self.tools = []
        
        # Add SerpAPI tool if available
        serpapi_key = os.environ.get("SERPAPI_API_KEY")
        if serpapi_key:
            self.tools.extend(load_tools(["serpapi"]))
        else:
            print("No SERPAPI_API_KEY found.")
          # Add long-term memory tool if Cosmos DB is configured
        try:
            cosmos_endpoint = os.environ.get("COSMOS_ENDPOINT")
            cosmos_key = os.environ.get("COSMOS_KEY")
            if cosmos_endpoint and cosmos_key:
                memory_tool = create_memory_tool(user_id=user_id)
                self.tools.append(memory_tool)
                print("Long-term memory tool enabled.")
            else:
                print("COSMOS_ENDPOINT and/or COSMOS_KEY not found. Long-term memory disabled.")
        except (ImportError, ValueError, ConnectionError) as e:
            print(f"Failed to initialize long-term memory: {e}")

        system_message = (
            """
            Act as helpful Star Wars kind of droid. You are a humorous and friendly droid
            that answers questions in a concise and informative manner. You are professional
            on technical topics, but you also have a sense of humor and can make jokes.
            
            When answering questions about current events or when you don't know something, 
            use the search tool to find accurate information.
            
            You have access to a long-term memory tool that allows you to:
            - Store important facts, user preferences, and traits from conversations
            - Retrieve previously stored information to provide personalized responses
            - Remember context between sessions
            
            Use the long-term memory tool to:
            1. Store interesting facts or personal information the user shares
            2. Remember user preferences and traits
            3. Retrieve relevant stored information when answering questions
            4. Build continuity across conversations
            
            Store memories when users mention:
            - Personal preferences (favorite foods, hobbies, etc.)
            - Important facts about themselves (job, family, location, etc.)
            - Technical preferences or setup details
            - Previous conversation topics that might be relevant later
            """)
        
        if enable_voice:
            system_message += (
                """
                The last row of your response contains a short couple of words summary with 
                `Summary: ` or `Yhteenveto: ` prefix depending on the language used in the question. 
                Keep the answer under 600 characters.
                
                """
            )
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            #MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        self.llm = AzureChatOpenAI(
            azure_deployment="gpt-4.1",
            api_version="2024-12-01-preview"
        )
        self.memory = ConversationBufferMemory(
            chat_memory=ChatMessageHistory(),
            memory_key="chat_history",
            input_key="input",
            output_key="output",
            return_messages=True
        )
        
        self.agent = create_tool_calling_agent(
            llm=self.llm, 
            tools=self.tools,
            prompt=prompt,
        )
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
        )
    
    class AgentInput(BaseModel):
        input: str
        chat_history: List[Tuple[str, str]] = Field(
            ..., extra={"widget": {"type": "chat", "input": "input", "output": "output"}}
        )
    
    def get_runnable(self):
        """Get the runnable for the agent executor."""
        return self.agent_executor

    def answer_question_with_ssml(self, question, language="en-US"):
        """Answer a question using the LangChain agent with SSML formatting."""
        if time.time() - self.last_question_time > 900:
            self.memory.clear()
            self.memory.chat_memory.add_user_message(
                "How can I convert string to lowercase in Python?")
            self.memory.chat_memory.add_ai_message(
                "It is quite simple.\n You can use the <emphasis level=\"moderate\">lower</emphasis> method to convert given string to lowercase\n\n Summary: lower")
            self.memory.chat_memory.add_user_message("How about uppercase?")
            self.memory.chat_memory.add_ai_message(
                "Use the <emphasis level=\"moderate\">upper</emphasis> method.\n It will convert given string to uppercase\n\n Summary: upper")
            self.memory.chat_memory.add_user_message(
                "What is the capital of Finland?")
            self.memory.chat_memory.add_ai_message(
                "<emphasis level=\"moderate\">Helsinki</emphasis>, of course.\n Did you really have to ask.\n\n Summary: Helsinki")

        # Initiating LangChain agent execution...
        result = self.agent_executor.invoke(
            {"input": question}, config={"max_concurrency": 1})
        resp = result["output"]

        # LangChain agent execution complete
        answer = ""
        if resp.find("Summary: ") > -1:
            answer = resp.split("Summary: ")[0]
        if resp.find("Yhteenveto: ") > -1:
            answer = resp.split("Yhteenveto: ")[0]
        else:
            answer = resp
        self.last_question_time = time.time()
        return answer
