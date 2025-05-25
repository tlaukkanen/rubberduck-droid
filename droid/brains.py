"""
Rubber Duck Droid - A Raspberry Pi powered AI assistant
"""
import faulthandler
import json
import os
import random
import subprocess
import time
from threading import Event, Thread

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
import pvporcupine
from pvrecorder import PvRecorder

from .display import Face, SummaryScreen
from droid.agent import DroidAgent

load_dotenv()

faulthandler.enable()
face = Face()
summary_screen = SummaryScreen()

# LangChain will get the API key from the environment variable OPENAI_API_KEY

class RubberDuckSpeechService():
  def __init__(self, device_name=None, language="en-US"):
    # Requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    self._device_name = device_name
    self._speech_config = speechsdk.SpeechConfig(
      subscription=os.environ.get('SPEECH_KEY'),
      region=os.environ.get('SPEECH_REGION')
    )
    self._speech_config.speech_recognition_language = language

  def recognize_from_microphone(self):
    print("Speak into your microphone.")
    summary_screen.showText("Listening...")
    #audio_config = speechsdk.audio.AudioConfig()#device_name=self._device_name)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self._speech_config)
    #, audio_config=audio_config)
    
    speech_recognition_result = speech_recognizer.recognize_once()
    #print("Done. speech_recognition_result: {}".format(speech_recognition_result))

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
      recognized_text = speech_recognition_result.text
      print("Recognized: {}".format(recognized_text))
      return recognized_text
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
      print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
      cancellation_details = speech_recognition_result.cancellation_details
      print("Speech Recognition canceled: {}".format(cancellation_details.reason))
      if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))
        print("Did you set the speech resource key and region values?")

  def speak(self, text, language="en-GB"):
    """Speak the given text using Azure Cognitive Services Text-to-Speech."""
    audio_config = speechsdk.audio.AudioOutputConfig(device_name="sysdefault:CARD=wm8960soundcard")# filename="temp_speech.wav") #device_name="sysdefault:CARD=wm8960soundcard") #device_name=self._device_name)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self._speech_config, audio_config=audio_config)
    lang_model = "en-GB-ThomasNeural"
    lang_code = "en-GB"
    if language == "fi-FI":
      lang_model = "fi-FI-HarriNeural"
      lang_code = "fi-FI"
    text_to_speak = "<speak xmlns=\"http://www.w3.org/2001/10/synthesis\" " \
      "xmlns:mstts=\"http://www.w3.org/2001/mstts\" " \
      "xmlns:emo=\"http://www.w3.org/2009/10/emotionml\" " \
      "version=\"1.0\" xml:lang=\"" + lang_code + "\">" \
      "<voice name=\"" + lang_model + "\">" + text + "</voice>" \
      "</speak>"

    print("Speaking: {}".format(text_to_speak))
    result = speech_synthesizer.speak_ssml_async(text_to_speak).get()
    if result.reason == speechsdk.ResultReason.Canceled:
      cancellation_details = result.cancellation_details
      print("Speech synthesis canceled: {}".format(cancellation_details.reason))  
      if cancellation_details.reason == speechsdk.CancellationReason.Error:  
        if cancellation_details.error_details:  
          print("Error details: {}".format(cancellation_details.error_details))  
          print("Did you set the speech resource key and region values?")
    # Play wav file - had to do it this way as I couldn't get AudioOutputConfig to work with PulseAudio
    # and I needed PulseAudio for getting the LED to work based on VU metering
    print("Done. result: {}".format(result))
    print("Playing audio through PulseAudio...")
    #with subprocess.Popen(("paplay", "temp_speech.wav")) as proc:
    #  proc.wait()
    print("Done speaking.")

class RubberDuckWakeWordDetector():

  WAKEWORD_ENGLISH = 0
  WAKEWORD_FINNISH = 1
  
  def __init__(
    self,
    access_key
  ):
    self._access_key = access_key
    self.chat = DroidAgent(enable_voice=True, user_id="default_user")
    self.recorder = None
    
  def run(self):
    porcupine = None
    recorder = None
    try:
      porcupine = pvporcupine.create(
        access_key=self._access_key,
        keyword_paths=["droid/Hi-droid_en_raspberry-pi_v3_0_0.ppn"]
      )
      
      devices = PvRecorder.get_available_devices()
      device_index = 1 #15
      device_name = "Built-in Audio Multichannel"
      for i in range(len(devices)):
         print('index: %d, device name: %s' % (i, devices[i]))
      #   # If device name contains wm8960-soundcard, use that device
      #   if devices[i].find('wm8960-soundcard') != -1:
      #     device_index = i
      #     device_name = devices[i]
      #     break
      summary_screen.showText("RubberDuck Droid\nv0.3.0")
      time.sleep(1)

      speech_service = RubberDuckSpeechService()#device_name="sysdefault:CARD=wm8960soundcard")
      #speech_service.speak(text="Ready in five seconds.")
      #time.sleep(5)
      #speech_service.speak(text="five")
      #time.sleep(5)
      speech_service.speak(text="I'm ready")
      time.sleep(0.5)

      recorder = PvRecorder(device_index=device_index, frame_length=porcupine.frame_length)
      recorder.start()
      print('Listening for wake word...')
      summary_screen.showText("Wake me by saying:\nHi Droid!")

      while True:
        pcm = recorder.read()
        result = porcupine.process(pcm)
        if result >= 0:
          print('Wakeword {} detected. Stopping wake word detector.'.format(result))
          recorder.stop()
          # Stop & delete recorder to free up microphone to speech recognizer
          recorder.delete()
          recorder = None
          time.sleep(0.2)
          # Determine language based on wakeword detected
          lang_code = "en-US"
          if result == RubberDuckWakeWordDetector.WAKEWORD_FINNISH:
            lang_code = "fi-FI"

          print('Starting speech recognizer.')
          summary_screen.showText("Listening... (" + lang_code + ")")

          speech_service = RubberDuckSpeechService(
            device_name="Built-in Audio Multichannel",
            language=lang_code)#device_name="sysdefault:CARD=wm8960soundcard")
          #speech_service.speak(text="Hello, I'm Rubber Duck. Ask me a question.")
          #return
          while True:
            question = speech_service.recognize_from_microphone()
            if question is None or question == "":
              break
            if question.lower().startswith("exit"):
              print("Exiting...")
              return
            else:
              print('Prompt GPT with user input: %s' % question)
              response = self.chat.answer_question_with_ssml(question, language=lang_code)
              summary_screen.showText(self.chat.summary)
              print('GPT response: %s' % response)
              speech_service.speak(text=response, language=lang_code)

          time.sleep(0.8)
          print('Starting wake word detector.')
          summary_screen.showText("Say:\nHi Droid!")
          recorder = PvRecorder(device_index=device_index, frame_length=porcupine.frame_length)
          recorder.start()
    except pvporcupine.PorcupineActivationError as e:
      print("AccessKey activation error")
      raise e
    except pvporcupine.PorcupineActivationLimitError as e:
      print("AccessKey '%s' has reached it's temporary device limit" % self._access_key)
      raise e
    except pvporcupine.PorcupineActivationRefusedError as e:
      print("AccessKey '%s' refused" % self._access_key)
      raise e
    except pvporcupine.PorcupineActivationThrottledError as e:
      print("AccessKey '%s' has been throttled" % self._access_key)
      raise e
    except pvporcupine.PorcupineError as e:
      print("Failed to initialize Porcupine")
      raise e
    except KeyboardInterrupt:
      print('Stopping ...')
    finally:
      if porcupine is not None:
        porcupine.delete()
      if recorder is not None:
        recorder.delete()

def displayFace(event):
  while not event.is_set():
    face.drawEyes()
    time.sleep(random.randint(1,3))
  face.poweroff()

def main():
  try:
    RubberDuckWakeWordDetector(
      access_key=os.environ.get('PORCUPINE_ACCESS_KEY')
    ).run()
  except KeyboardInterrupt:
    print('Exiting...')
    face.poweroff()

#if __name__ == '__main__':
stop_event = Event()
face_thread = Thread(target=displayFace, args=(stop_event,), daemon=True)
try:
  #print("Starting VU meter thread...")
  #vumeter_thread = Thread(target=vumeter.vumeter)
  #vumeter_thread.start()
  print("Starting Rubber Duck display thread...")
  face_thread.start()
  print("Starting Rubber Duck wake word detector thread...")
  main()
  #vumeter.vumeter()

except KeyboardInterrupt:
  print('Exiting...')
finally:
  stop_event.set()
  face_thread.join()
  summary_screen.poweroff()
  
