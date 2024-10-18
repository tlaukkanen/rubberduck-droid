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

Copy .env.template to .env and define environment variables:
- SPEECH_KEY=<Azure text-to-speech API key>
- OPENAI_API_KEY=<OpenAI API key>
- SPEECH_REGION<Azure region for your Speech service>
- PORCUPINE_ACCESS_KEY=<Porcupine access key for speech-to-text>

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

Start the droid:

```sh
python3 main.py
```

# Wakeword files

There most likely are copyright issues with the PicoVoice wake word files so didn't include those to the repo. You can create your own .ppn files in PicoVoice console. It's really easy to use. Just select what word you want to train it for and select Raspberry Pi as your platform. That'll generate the .ppn file for you. Check it out at: https://console.picovoice.ai/