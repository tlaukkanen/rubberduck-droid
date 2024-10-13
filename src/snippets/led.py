import RPi.GPIO as GPIO
import time

LED_PIN = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
print("LED on")
GPIO.output(LED_PIN, GPIO.HIGH)
time.sleep(5)
print("LED off")
GPIO.output(LED_PIN, GPIO.LOW)