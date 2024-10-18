import os
import pvporcupine
from pvrecorder import PvRecorder

class WakeWordDetector():

  WAKEWORD_ENGLISH = 0
  WAKEWORD_FINNISH = 1
  

  def __init__(
    self,
    access_key
  ):
    self._access_key = access_key
    self.recorder = None
    
  def wait_for_wake_word(self):
    porcupine = None
    try:
      current_dir = os.path.dirname(os.path.abspath(__file__))
      keyword_file1 = os.path.join(current_dir, "Hey-Rubber-Duck_en_raspberry-pi_v2_2_0.ppn")      
      keyword_file2 = os.path.join(current_dir, "Hey-Droid_en_raspberry-pi_v2_2_0.ppn")
      
      porcupine = pvporcupine.create(
        access_key=self._access_key,
        keyword_paths=[keyword_file1, keyword_file2]
      )
      
      devices = PvRecorder.get_available_devices()  #.get_audio_devices()
      device_index = 1
      device_name = "Built-in Audio Multichannel"
      # for i in range(len(devices)):
      #    print('index: %d, device name: %s' % (i, devices[i]))
      #    # If device name contains wm8960-soundcard, use that device
      #    if devices[i].find('wm8960-soundcard') != -1:
      #      device_index = i
      #      device_name = devices[i]
      #      break
      print('Using device: %s' % device_name)
      recorder = PvRecorder(device_index=device_index, frame_length=porcupine.frame_length)
      recorder.start()
      print('Listening for wake word...')

      while True:
        pcm = recorder.read()
        result = porcupine.process(pcm)
        if result >= 0:
          print('Wakeword {} detected. Stopping wake word detector.'.format(result))
          recorder.stop()
          # Stop & delete recorder to free up microphone to speech recognizer
          recorder.delete()
          recorder = None
          
          return True

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