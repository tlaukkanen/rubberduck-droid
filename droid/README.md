# DroidAgent CLI Usage

You can use the DroidAgent (Star Wars droid chat agent) without speech capabilities via a simple CLI:

```bash
poetry run python -m droid.agent.cli
```

Type your questions and chat with the DroidAgent. Type `exit` to quit.

The agent uses LangChain and Azure OpenAI (see environment variables in the main project README).

# Rubberduck Droid

Azure OpenaI Realtime code is mostly based on sample code from [aoai-realtime-audio-sdk](https://github.com/Azure-Samples/aoai-realtime-audio-sdk).

## Setting Constants
The constants defined in `voice_chat.py` configure the sample rate and chunk size for the microphone and speakers.  
Adjust these settings according to your environment if needed:
```python
INPUT_SAMPLE_RATE = 16000  # Input sample rate
INPUT_CHUNK_SIZE = 512  # Input chunk size
OUTPUT_SAMPLE_RATE = 24000  # Output sample rate **Must be set to 24000**
OUTPUT_CHUNK_SIZE = 1024  # Output chunk size
STREAM_FORMAT = pyaudio.paInt16  # Stream format
INPUT_CHANNELS = 1  # Input channels
OUTPUT_CHANNELS = 1  # Output channels
```

The logs are stored in the 'log' directory. The logs contain timestamps for Client Events and Server Events.

## Dialogue
In addition to voice dialogue, `dialogue.py` implements the following features:

- Function execution
- Conversation termination (session reset)

This allows for more versatile conversations, and at the same time, when a conversation ends, it enables the session to restart, which is expected to reduce token costs.

## Reference Links
- [Azure-Samples/aoai-realtime-audio-sdk](https://github.com/Azure-Samples/aoai-realtime-audio-sdk/tree/main/python)
