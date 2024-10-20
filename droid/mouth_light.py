
import asyncio
import RPi.GPIO as GPIO

class MouthLight:
    def __init__(self, pin=26):
        self.LED_PIN = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.LED_PIN, GPIO.OUT)

    async def show_light(self, duration: float):
        GPIO.output(self.LED_PIN, GPIO.HIGH)
        await asyncio.sleep(duration)
        print("LED off")
        GPIO.output(self.LED_PIN, GPIO.LOW)
        GPIO.cleanup()
        print("LED off")

# Example usage:
# mouth_light = MouthLight()
# asyncio.run(mouth_light.show_light(5.0))