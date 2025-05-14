import os
import time
from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.memory import ConversationBufferMemory
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.utilities import SerpAPIWrapper

class DroidAgent:
    def _create_dummy_search_tool(self):
        @tool
        def search(query: str) -> str:
            """Useful for when you need to answer questions about current events or search for specific information."""
            return "I'm sorry, I don't have access to web search at the moment. Please provide a SERPAPI_API_KEY in the environment variables to enable this feature."
        return [search]

    def __init__(self):
        self.last_question_time = time.time()
        serpapi_key = os.environ.get("SERPAPI_API_KEY")
        if serpapi_key:
            try:
                self.tools = load_tools(["serpapi"])
            except Exception:
                try:
                    search_wrapper = SerpAPIWrapper()
                    @tool
                    def search(query: str) -> str:
                        return search_wrapper.run(query)
                    self.tools = [search]
                except Exception:
                    self.tools = self._create_dummy_search_tool()
        else:
            self.tools = self._create_dummy_search_tool()

        system_message = (
            "Act as humorous Star Wars droid. Answer each "
            "sentence in your own line separated by newline character. "
            "Sentences can include speech synthesis markup language (SSML) "
            "emphasis tags. The last row contains a short couple of words summary. "
            "Keep the answer under 600 characters.\n\n"
            "When answering questions about current events or when you don't know something, "
            "use the search tool to find accurate information."
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        self.llm = AzureChatOpenAI(
            azure_deployment="o4-mini",
            api_version="2024-12-01-preview"
        )
        self.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
        # Add example interactions to memory for few-shot learning
        self.memory.chat_memory.add_user_message("How can I convert string to lowercase in Python?")
        self.memory.chat_memory.add_ai_message("It is quite simple.\n You can use the <emphasis level=\"moderate\">lower</emphasis> method to convert given string to lowercase\n\n Summary: lower")
        self.memory.chat_memory.add_user_message("How about uppercase?")
        self.memory.chat_memory.add_ai_message("Use the <emphasis level=\"moderate\">upper</emphasis> method.\n It will convert given string to uppercase\n\n Summary: upper")
        self.memory.chat_memory.add_user_message("What is the capital of Finland?")
        self.memory.chat_memory.add_ai_message("<emphasis level=\"moderate\">Helsinki</emphasis>, of course.\n Did you really have to ask.\n\n Summary: Helsinki")
        self.agent = create_tool_calling_agent(llm=self.llm, tools=self.tools, prompt=prompt)
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
        )

    def answer_question_with_ssml(self, question, language="en-US"):
        if time.time() - self.last_question_time > 900:
            self.memory.clear()
            self.memory.chat_memory.add_user_message("How can I convert string to lowercase in Python?")
            self.memory.chat_memory.add_ai_message("It is quite simple.\n You can use the <emphasis level=\"moderate\">lower</emphasis> method to convert given string to lowercase\n\n Summary: lower")
            self.memory.chat_memory.add_user_message("How about uppercase?")
            self.memory.chat_memory.add_ai_message("Use the <emphasis level=\"moderate\">upper</emphasis> method.\n It will convert given string to uppercase\n\n Summary: upper")
            self.memory.chat_memory.add_user_message("What is the capital of Finland?")
            self.memory.chat_memory.add_ai_message("<emphasis level=\"moderate\">Helsinki</emphasis>, of course.\n Did you really have to ask.\n\n Summary: Helsinki")
        print(f"Prompt: {question}")
        print("Initiating LangChain agent execution...")
        result = self.agent_executor.invoke({"input": question}, config={"max_concurrency": 1})
        resp = result["output"]
        print("LangChain agent execution complete.")
        print(f"Agent response: {resp}")
        summary = "-"
        answer = ""
        if resp.find("Summary: ") > -1:
            summary = "Summary:\n" + resp.split("Summary: ")[1]
            answer = resp.split("Summary: ")[0]
        if resp.find("Yhteenveto: ") > -1:
            summary = "Yhteenveto:\n" + resp.split("Yhteenveto: ")[1]
            answer = resp.split("Yhteenveto: ")[0]
        print(f"Summary: {summary}")
        self.last_question_time = time.time()
        return answer
