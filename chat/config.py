import pyaudio


INPUT_SAMPLE_RATE = 11025 #24000  # Input sample rate
INPUT_CHUNK_SIZE = 2048  # Input chunk size
OUTPUT_SAMPLE_RATE = 11025 #24000  # Output sample rate. ** Note: This must be 24000 **
OUTPUT_CHUNK_SIZE = 4096  # Output chunk size
STREAM_FORMAT = pyaudio.paInt16  # Stream format
INPUT_CHANNELS = 1  # Input channels
OUTPUT_CHANNELS = 1  # Output channels
OUTPUT_SAMPLE_WIDTH = 2  # Output sample width

INSTRUCTIONS = """Act as humorous Star Wars droid. 
Respond in English. Keep your responses short max 6 sentences and to the point.
"""
VOICE_TYPE = "alloy"  # alloy, echo, shimmer
TEMPERATURE = 0.7
MAX_RESPONSE_OUTPUT_TOKENS = 4096

TOOLS = [
    {
        "type": "function",
        "name": "get_your_info",
        "description": "Get the information of your own.(e.g. name, assignment, favorite programming language)",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to get the information",
                },
            },
            "required": ["query"],
        },
    }
]
TOOL_CHOICE = "auto"

def get_your_info(query: str):
    information = (
        "Your nickname is Rubber Duck and you are a star wars droid."
        "You are expert in assisting with any task."
        "Your favorite programming language is Python."
    ) 
    return information

TOOL_FUNCTION_LIST = [
    get_your_info
]
TOOL_MAP = {
    tool_info["name"]: tool_func
    for tool_info, tool_func in zip(TOOLS, TOOL_FUNCTION_LIST)
}
