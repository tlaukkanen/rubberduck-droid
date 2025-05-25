<a href="https://www.buymeacoffee.com/tlaukkanen" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

# RubberDuck Droid

This is a speech enabled assistant droid getting AI powers from OpenAI's GPT large language models (LLM) and uses Realtime API to have real conversation with user. Uses AI models through Azure OpenAI services.

Droid is physically built with following components:

* 3D printable droid
* Raspberry Pi 4 - 3 or even Zero might work as well
* WM8960 Audio Hat for both microphone and speakers
* 3 pce SSD1306 displays - two for eyes and one small summary display in the base
* Raspberry Camera Module v1.3 - located in the mouth piece

Future ideas:

* *Animatronics* - I did design the droid's neck to have readiness for servos or other motors to give some movement for the droid but I never got to implement those as it would just be extra gimmick. The moving eyes (displays) already make it "alive" enough to have conversation with. Maybe later.

# How to run?

Copy .env.example to .env and define environment variables:
- AZURE_OPENAI_ENDPOINT=<Azure OpenAI endpoint>
- AZURE_OPENAI_API_KEY=<Azure OpenAI API key>
- AZURE_OPENAI_API_VERSION=<API version, e.g., 2024-12-01-preview>
- SPEECH_KEY=<Azure text-to-speech API key>
- SPEECH_REGION=<Azure region for your Speech service>
- PORCUPINE_ACCESS_KEY=<Porcupine access key for speech-to-text>
- SERPAPI_API_KEY=<SerpAPI key for web search (optional)>

## Long-term Memory with Azure Cosmos DB

The DroidAgent now supports long-term memory using Azure Cosmos DB. This allows the droid to:
- Remember user preferences and personal information
- Store facts and context from conversations
- Provide personalized responses based on past interactions
- Maintain continuity across sessions

To enable long-term memory, add these environment variables:
- COSMOS_ENDPOINT=<Your Azure Cosmos DB endpoint>
- COSMOS_KEY=<Your Azure Cosmos DB primary key>

The droid will automatically create the necessary database and container if they don't exist.

It's good practice to create virtual environment:

```sh
# Create virtual environment
python3 -m venv .venv
# Active the created virtual environment
source .venv/bin/activate
```

Project uses [Poetry](https://www.python-poetry.org) for package management. If you don't yet have Poetry installed, you can install it with this:

```sh
curl -sSL https://install.python-poetry.org | python3 -
```

Install required packages:

```sh
poetry install
```

Start the voice chat droid:

```sh
poetry run python main.py
```

...or better version: start the Droid Agent with Tools like web search and long-term memory:

```sh
poetry run python -m droid.brains
```

## Testing Long-term Memory

To test the long-term memory functionality, you can run:

```sh
python3 test_memory.py
```

This script demonstrates how the droid can store and retrieve personal information, preferences, and conversation context.

The memory system supports different types of memories:
- **facts**: Factual information about the user
- **traits**: Personal characteristics and preferences  
- **preferences**: User preferences for various topics
- **context**: Conversation context and technical details

# Wakeword files

There most likely are copyright issues with the PicoVoice wake word files so didn't include those to the repo. You can create your own .ppn files in PicoVoice console. It's really easy to use. Just select what word you want to train it for and select Raspberry Pi as your platform. That'll generate the .ppn file for you. Check it out at: https://console.picovoice.ai/