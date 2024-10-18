import asyncio
import os
import random
import threading
from dotenv import load_dotenv
from chat.voice_chat import with_azure_openai
from droid.display import SummaryScreen, Face
from droid.wake_word_detector import WakeWordDetector

load_dotenv()

def get_env_var(var_name: str) -> str:
    value = os.environ.get(var_name)
    if not value:
        raise OSError(f"Environment variable '{var_name}' is not set or is empty.")
    return value

summary_screen = SummaryScreen()
face = Face()
wake_word_detector = WakeWordDetector(access_key=get_env_var("PORCUPINE_ACCESS_KEY"))

async def displayFace(event):
    try:
        while not event.is_set():
            #face.drawEyes()
            face.drawSleepyEyes()
            await asyncio.sleep(random.randint(1, 3))
    finally:
        face.poweroff()  # Ensure this runs when the loop ends or on interrupt

async def main():
    event = threading.Event()  # Event for stopping the loop

    summary_screen.showText("Wake me by saying\n'Hey Droid!'")
    
    # Start the displayFace function asynchronously
    display_task = asyncio.create_task(displayFace(event))
    
    try:
        await display_task
        # Wait until wake word is detected
        wake_detected = wake_word_detector.wait_for_wake_word()
        if wake_detected:
            summary_screen.showText("Yes, how can I help?")
            #await with_azure_openai()
        else:
            summary_screen.showText("I am going to sleep now.")

        await asyncio.sleep(5)  # Simulate running for 10 seconds
        
    except asyncio.CancelledError:
        pass  # Handle task cancellation if needed
    except KeyboardInterrupt:
        print("CTRL+C pressed, stopping...")
    finally:
        # Set the event to stop displayFace and wait for it to finish
        event.set()
        summary_screen.poweroff()
        

if __name__ == "__main__":
    try:
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("Application interrupted by user.")