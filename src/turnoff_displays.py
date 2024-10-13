import time
import random
import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

def circle(self: ImageDraw, color, x, y, r):
  self.ellipse((x,y,x+r,y+r),fill=color)    
  self.ellipse((x+2,y+2,x+r-2,y+r-2),fill=0)    
  self.ellipse((x+6,y+6,x+r-6,y+r-6),fill=color)
  self.ellipse((x+12,y+12,x+r-12,y+r-12),fill=0)    
ImageDraw.rounded_rectangle = circle

class Face:
  def __init__(self):

    # Setting some variables for our reset pin etc.
    RESET_PIN = digitalio.DigitalInOut(board.D4)

    self.i2c = board.I2C()
    self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, self.i2c, addr=0x3C, reset=RESET_PIN)
    self.oled.rotate(2)

    # Clear display
    self.oled.fill(0)
    self.oled.show()

    self.width = 128
    self.height = 64

    # Create blank image for drawing.
    self.image = Image.new("1", (128, 64))
    self.draw = ImageDraw.Draw(self.image)
    self.draw.circle = circle
    # Load a font in 2 different sizes.
    self.font = ImageFont.truetype("fonts/EarlyGameBoy.ttf", 8)

  def drawEyes(self):
    x = random.randint(35, 45)
    y = random.randint(0, 16)

    # Draw a black filled box to clear the image.
    self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    self.draw.circle(self.draw, 255, x, y, 48)
    #self.draw.rectangle((x, y+30, x+10, y+40), outline=0, fill=0)
    
    #self.draw.text((5, 0), "PROTOTYPE v0.2", font=self.font, fill=255)
    
    self.oled.image(self.image)
    self.oled.show()

  def drawBlinkEyes(self):
    if not random.randint(0,3) % 2:
      self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
      self.draw.rectangle((x+9, y+4, x+11, y+16), outline=0, fill=256)
      self.oled.image(self.image)
      self.oled.show()

  def poweroff(self):
    self.oled.poweroff()

face = Face()
# try:
#   while True:
#     face.drawEyes()
#     time.sleep(random.randint(1,3))
# except KeyboardInterrupt:
face.poweroff()
