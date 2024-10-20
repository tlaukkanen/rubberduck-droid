import asyncio
import os
import random
from dotenv import load_dotenv
from droid.voice_chat import start_realtime_chat
from droid.display import SummaryScreen, Face
from droid.wake_word_detector import WakeWordDetector

load_dotenv()

def get_env_var(var_name: str) -> str:
    value = os.environ.get(var_name)
    if not value:
        raise OSError(f"Environment variable '{var_name}' is not set or is empty.")
    return value

# Small display in the torso - capable to display text
summary_screen = SummaryScreen()
# Two eyes on the face
face = Face()
# Wake word detector (Porcupine - https://picovoice.ai/docs/quick-start/porcupine-raspberrypi/)
wake_word_detector = WakeWordDetector(access_key=get_env_var("PORCUPINE_ACCESS_KEY"))
is_sleeping = True

async def displayFace(event: asyncio.Event):
    global is_sleeping
    try:
        print("start eye displays")
        while not event.is_set():
            if is_sleeping:
                face.drawSleepyEyes()
            else:
                face.drawEyes()
            await asyncio.sleep(random.randint(1, 3))
    finally:
        face.poweroff()  # Ensure this runs when the loop ends or on interrupt

async def main():
    exit_event = asyncio.Event()  # Event for stopping the loop

    summary_screen.showText("Wake me by saying\n'Hey Droid!'")
    
    # Start the displayFace function asynchronously
    display_task = asyncio.create_task(displayFace(exit_event))
    await asyncio.sleep(1)
    
    try:
        # How to start this task asynchronously?
        #await display_task
        print("start wake detection")
        while not exit_event.is_set():
            # Wait until wake word is detected
            wake_detection_task = asyncio.create_task(wake_word_detector.wait_for_wake_word())
            wake_detected = await wake_detection_task
            if wake_detected:
                summary_screen.showText("How can I help?")
                await start_realtime_chat()
                summary_screen.showText("Sleepy time.")
                await asyncio.sleep(1)
            else:
                summary_screen.showText("I am going to sleep now.")
        
    except asyncio.CancelledError:
        pass  # Handle task cancellation if needed
    except KeyboardInterrupt:
        print("CTRL+C pressed, stopping...")
    finally:
        # Set the event to stop displayFace and wait for it to finish
        exit_event.set()
        summary_screen.poweroff()

if __name__ == "__main__":
    try:
        print("Starting main loop with asyncio...")
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("Application interrupted by user.")