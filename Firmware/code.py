#settings.toml config:
#CIRCUITPY_WIFI_SSID = "insert ssid here"
#CIRCUITPY_WIFI_PASSWORD = "insert passsord here"
#WEATHER_URL = "insert URL here"

#Imports
import board
import terminalio #font
import displayio
from adafruit_display_text import label #Allows for text
from adafruit_st7735r import ST7735R #Need to change to ST7735 for acutal firmware, this is for testing on the Sprig
from fourwire import FourWire #For SPI connection
import busio #For SPI connection
from digitalio import DigitalInOut, Direction, Pull #For buttons (encoder will be added later)
import adafruit_requests #For webscraping
import wifi
import os #For wifi passwords, etc
import socketpool
import ssl
import time

#Weather URL
weatherURL = os.getenv('WEATHER_URL')

#Connect to WiFi
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# Release any resources currently in use for the displays
displayio.release_displays()

#Setup pins
spi = busio.SPI(clock=board.GP18, MOSI=board.GP19, MISO=board.GP16) #Need to change pins for ESP32
tft_cs = board.GP20 #Need to change pins for ESP32
tft_dc = board.GP22 #Need to change pins for ESP32
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.GP26) #Need to change pins for ESP32
display = ST7735R(display_bus, width=128, height=160, rotation=180, bgr=True) #Remove R from library name for final version

# Make the display context
splash = displayio.Group()
display.root_group = splash
color_bitmap = displayio.Bitmap(128, 160, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000  #Black bg

#Black background
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

#Setup button
btn = DigitalInOut(board.GP5) #Change this for the ESP32
btn.direction = Direction.INPUT #Sets the button to be an input
btn.pull = Pull.UP

# Draw a label
text_group = displayio.Group(scale=1, x=4, y=7)
text = label.Label(terminalio.FONT, text="Loading...", color=0xFFFFFF)
text_group.append(text)  # Subgroup for text scaling
splash.append(text_group)

while True: #Keep refreshing
    response = requests.get(weatherURL)
    responseJSON = response.json()
    #MUST BE IN ONE LINE, OTHERWISE IT'LL GET MAD AND THROW AN ERROR IDK WHY
    text.text = str(responseJSON['current']['temperature_2m']) + "°F" + "\n"+ "Feels like: " + str(responseJSON['current']['apparent_temperature']) + "°F"
    time.sleep(300)