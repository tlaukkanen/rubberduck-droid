# RubberDuck Droid

This is a speech enabled assistant droid getting AI powers from OpenAI's GPT-4 large language model (LLM) and using speech capabilities of Azure Cognitive Services to provide speech-to-text recognition as well as text-to-speech synthesis for droid's responses.

Droid is built with following components:

* Raspberry Pi 4 - 3 or even Zero might work as well
* WM8960 Audio Hat for both microphone and speakers
* 3 pce SSD1306 displays - two for eyes and one small summary display in the base
* Raspberry Camera Module v1.3 - located in the mouth piece

Future ideas:

* *Animatronics* - I did design the droid's neck to have readiness for servos or other motors to give some movement for the droid but I never got to implement those as it would just be extra gimmick. The moving eyes (displays) already make it "alive" enough to have conversation with. Maybe later.

# How to run?

Define environment variables:
- SPEECH_KEY=<Azure text-to-speech API key>
- OPENAI_API_KEY=<OpenAI API key>
- SPEECH_REGION<Azure region for your Speech service>
- PORCUPINE_ACCESS_KEY=<Porcupine access key for speech-to-text>

You can run the project with Python:

```sh
> cd src/
> python src/brains.py
```

# Wakeword files

There most likely are copyright issues with the PicoVoice wake word files so didn't include those to the repo. You can create your own .ppn files in PicoVoice console. It's really easy to use. Just select what word you want to train it for and select Raspberry Pi as your platform. That'll generate the .ppn file for you. Check it out at: https://console.picovoice.ai/