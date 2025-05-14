import faulthandler
import json
import os
import random
import subprocess
import time
from threading import Event, Thread

import azure.cognitiveservices.speech as speechsdk
import pvporcupine
from pvrecorder import PvRecorder

from langchain_openai import AzureChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.memory import ConversationBufferMemory
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.utilities import SerpAPIWrapper

#import vumeter
from display import Face, SummaryScreen

faulthandler.enable()
face = Face()
summary_screen = SummaryScreen()

PROMPT_MESSAGES_EN = [
  {
    "role": "system",
    "content": "Act as humorous Star Wars droid. Answer each " \
      "sentence in your own line separated by newline character. " \
      "Sentences can include speech synthesis markup language (SSML) " \
      "emphasis tags. The last row contains a short couple of words summary. " \
      "Keep the answer under 600 characters."
  },
  {
    "role": "user",
    "content": "How can I convert string to lowercase in Python?"
  },
  {
    "role": "assistant", 
    "content": "It is quite simple.\n You can use the " \
      "<emphasis level=\"moderate\">lower</emphasis> method to convert " \
      "given string to lowercase\n\n " \
      "Summary: lower" 
  },
  {
    "role": "user",
    "content": "How about uppercase?"
  },
  {
    "role": "assistant",
    "content": "Use the <emphasis level=\"moderate\">upper</emphasis> " \
      "method.\n It will convert given string to uppercase\n\n " \
      "Summary: upper"
  },
  {
    "role": "user",
    "content": "What is the capital of Finland?"
  },
  {
    "role": "assistant",
    "content": "<emphasis level=\"moderate\">Helsinki</emphasis>, of course.\n " \
      "Did you really have to ask.\n\n " \
      "Summary: Helsinki"
  },
  {
    "role": "user",
    "content": "How many GPIO pins are there in Raspberry Pi?"
  },
  {
    "role": "assistant",
    "content": "Ah, the Raspberry Pi!\n " \
      "There are <emphasis level=\"moderate\">40</emphasis> GPIO pins in a Raspberry Pi board.\n\n" \
      "Summary: 40 pins"
  },
  {
    "role": "user",
    "content": "Is it possible to create a ticket to JIRA via REST API on behalf of the customer?"
  },
  {
    "role": "assistant",
    "content": "Oh, absolutely!\n To create a ticket in <emphasis level=\"moderate\">JIRA</emphasis> via its REST API on behalf of a customer, you'll need to use the <emphasis level=\"moderate\">Create Request endpoint</emphasis>. Just make sure you have the proper permissions and authentication!\n\n Summary: Create Request endpoint"
  }
]



class DroidAgent():
  def _create_dummy_search_tool(self):
    @tool
    def search(query: str) -> str:
        """Useful for when you need to answer questions about current events or search for specific information."""
        return "I'm sorry, I don't have access to web search at the moment. Please provide a SERPAPI_API_KEY in the environment variables to enable this feature."
    
    return [search]

  def __init__(self):
    self.last_question_time = time.time()
    
    # Check if SERPAPI_API_KEY is set in the environment
    serpapi_key = os.environ.get("SERPAPI_API_KEY")
    
    # Set up tools
    if serpapi_key:
      try:
        # Method 1: Using load_tools (preferred method)
        self.tools = load_tools(["serpapi"])
        print("Successfully loaded SerpAPI tool using load_tools")
      except Exception as e:
        print(f"Error loading SerpAPI with load_tools: {e}")
        try:
          # Method 2: Create tool manually
          search_wrapper = SerpAPIWrapper()
          
          @tool
          def search(query: str) -> str:
              """Useful for when you need to answer questions about current events or search for specific information."""
              return search_wrapper.run(query)
          
          self.tools = [search]
          print("Successfully created SerpAPI tool manually")
        except Exception as e:
          print(f"Error creating SerpAPI manually: {e}")
          self.tools = self._create_dummy_search_tool()
    else:
      print("SERPAPI_API_KEY not found in environment variables. Web search functionality is disabled.")
      self.tools = self._create_dummy_search_tool()
    
    # Define available tools
    #self.tools = [search]
    
    # Define system message with droid character and SSML formatting requirements
    system_message = """Act as humorous Star Wars droid. Answer each 
      sentence in your own line separated by newline character.
      Sentences can include speech synthesis markup language (SSML)
      emphasis tags. The last row contains a short couple of words summary.
      Keep the answer under 600 characters.
      
      When answering questions about current events or when you don't know something,
      use the search tool to find accurate information."""
    
    # Create the prompt template with system message and conversation history
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    
    # Initialize the language model
    self.llm = AzureChatOpenAI(
#        model="gpt-4.1",  # Updated model name for newer OpenAI client
        azure_deployment="o4-mini",
        api_version="2024-12-01-preview"
        #temperature=0.5,
        #frequency_penalty=0.5,
        #presence_penalty=0.2
    )
    
    # Set up conversation memory
    self.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    
    # Add example interactions to memory for few-shot learning
    self.memory.chat_memory.add_user_message("How can I convert string to lowercase in Python?")
    self.memory.chat_memory.add_ai_message("It is quite simple.\n You can use the <emphasis level=\"moderate\">lower</emphasis> method to convert given string to lowercase\n\n Summary: lower")
    
    self.memory.chat_memory.add_user_message("How about uppercase?")
    self.memory.chat_memory.add_ai_message("Use the <emphasis level=\"moderate\">upper</emphasis> method.\n It will convert given string to uppercase\n\n Summary: upper")
    
    self.memory.chat_memory.add_user_message("What is the capital of Finland?")
    self.memory.chat_memory.add_ai_message("<emphasis level=\"moderate\">Helsinki</emphasis>, of course.\n Did you really have to ask.\n\n Summary: Helsinki")
    

    # Try the newer API first
    self.agent = create_tool_calling_agent(llm=self.llm, tools=self.tools, prompt=prompt)
    
    # Try the newer executor creation method
    self.agent_executor = AgentExecutor.from_agent_and_tools(
        agent=self.agent,
        tools=self.tools,
        memory=self.memory,
        verbose=True,
    )

  def answer_question_with_ssml(self, question, language="en-US"):
    # Reset conversation history if it's been too long
    if time.time() - self.last_question_time > 900:  # 15 minutes
      self.memory.clear()
      # Re-add example interactions
      self.memory.chat_memory.add_user_message("How can I convert string to lowercase in Python?")
      self.memory.chat_memory.add_ai_message("It is quite simple.\n You can use the <emphasis level=\"moderate\">lower</emphasis> method to convert given string to lowercase\n\n Summary: lower")
      
      self.memory.chat_memory.add_user_message("How about uppercase?")
      self.memory.chat_memory.add_ai_message("Use the <emphasis level=\"moderate\">upper</emphasis> method.\n It will convert given string to uppercase\n\n Summary: upper")
      
      self.memory.chat_memory.add_user_message("What is the capital of Finland?")
      self.memory.chat_memory.add_ai_message("<emphasis level=\"moderate\">Helsinki</emphasis>, of course.\n Did you really have to ask.\n\n Summary: Helsinki")
    
    print("Prompt: {}".format(question))
    print("Initiating LangChain agent execution...")
    summary_screen.showText("Thinking...")
    
    # Generate the response using the agent
    result = self.agent_executor.invoke({"input": question}, config={"max_concurrency": 1})
    resp = result["output"]
    
    print("LangChain agent execution complete.")
    print("Agent response: {}".format(resp))
    
    # Extract summary from the response
    summary = "-"
    answer = ""
    if resp.find("Summary: ") > -1:
      summary = "Summary:\n" + resp.split("Summary: ")[1]
      answer = resp.split("Summary: ")[0]
    if resp.find("Yhteenveto: ") > -1:
      summary = "Yhteenveto:\n" + resp.split("Yhteenveto: ")[1]
      answer = resp.split("Yhteenveto: ")[0]
    
    print("Summary: {}".format(summary))
    summary_screen.showText(summary)
    
    # Update the last question time
    self.last_question_time = time.time()
    
    return answer

# LangChain will get the API key from the environment variable OPENAI_API_KEY

class RubberDuckSpeechService():
  def __init__(self, device_name=None, language="en-US"):
    # Requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    self._device_name = device_name
    self._speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
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
    self.chat = DroidAgent()
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
  
