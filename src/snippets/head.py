import time
from adafruit_servokit import ServoKit

# Just a placeholder for adding animatronics for the head

kit = ServoKit(channels=16)
neck = kit.servo[0]
neck.angle = 90

time.sleep(1)

neck.angle = 100

time.sleep(1)

neck.angle = 90

