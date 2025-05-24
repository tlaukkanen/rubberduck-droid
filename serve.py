# serve.py
"""
Entrypoint for running DroidAgent via LangServe.
Exposes HTTP API and interactive playground UI.
"""
from typing import Any
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from langserve import add_routes
from openai import BaseModel

from droid.agent.droid_agent import DroidAgent


# Instantiate the agent once at startup
droid_agent = DroidAgent(enable_voice=False)

app = FastAPI(
    title="RubberDuck DroidAgent API",
    version="1.0.0",
    description="Ask questions to your droid via HTTP or the auto-generated playground UI.",
)

# We need to add these input/output schemas because the current AgentExecutor
# is lacking in schemas.
class Input(BaseModel):
    """Input question for the droid agent."""
    input: str


class Output(BaseModel):
    """Output from the droid agent."""
    output: Any

add_routes(
    app,
    droid_agent.get_runnable(),
    input_type=Input,
    output_type=Output,
    path="/droid"
)

@app.post("/ask", summary="Get SSML-formatted answer")
async def ask(question: str, language: str = "en-US"):
    """
    Ask a question to the DroidAgent.

    - **question**: The user’s question text.
    - **language**: BCP-47 language tag for SSML (default: en-US).
    """
    answer = droid_agent.answer_question_with_ssml(question, language)
    return {"answer": answer}

app.mount("/", 
        StaticFiles(directory="chat-dist", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Launch Uvicorn via LangServe (includes Swagger UI at /docs)
    uvicorn.run(app, host="0.0.0.0", port=8000)
