import RPi.GPIO as GPIO
import time
import sys
import os
from hx711 import HX711
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
def cleanAndExit():
    print ("Cleaning...")
    GPIO.cleanup()
    print ("Bye!")
    sys.exit()


GAIN = 64

DATA_1 = 27
CLCK_1 = 17
hx1 = HX711(DATA_1, CLCK_1, gain=GAIN)
hx1.set_reading_format("LSB", "MSB")

hx1.set_reference_unit(92)

hx1.reset()

hx1.tare()


while True:
    try:
        val_1 = hx1.get_weight(DATA_1)
        print(val_1)
        time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
