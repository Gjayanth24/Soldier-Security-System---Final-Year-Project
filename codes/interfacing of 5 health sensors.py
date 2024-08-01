import time
import sys
import os
import RPi.GPIO as GPIO
from hx711 import HX711
from w1thermsensor import W1ThermSensor, Unit
import Adafruit_DHT
from max30102 import MAX30102
from heartrate_monitor import HeartRateMonitor

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

referenceUnit = 1
hbs_pin = 18
sensor = W1ThermSensor()
DHT_sensor = Adafruit_DHT.DHT11
DHT_pin = 5
HX711_DOUT_PIN = 27
HX711_SCK_PIN = 17
DHT_PIN = 5

GPIO.setup(hbs_pin, GPIO.IN)

EMULATE_HX711 = False

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()

    print("Bye!")
    sys.exit()

hx = HX711(HX711_DOUT_PIN, HX711_SCK_PIN)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()
print("Tare done! Add weight now...")
bc = 0


def get_HB_data():
    print('please wear HB sensor clip to your fingure')
    cnt = 0
    tempv = time.time()
    while time.time() < (tempv + 7):
        if GPIO.input(hbs_pin) == GPIO.LOW:
            cnt += 1
            time.sleep(0.4)
    cnt = cnt * 7
    heartrate = cnt
    cnt = 0
    return heartrate

while True:
    tp=0
    while(tp<10):
      val = hx.get_weight(5)/1000
      if(val<10):
          val=0
      if(val>20):
          bc=bc+1
          time.sleep(1)
      tp=tp+1
      print('Pres:'+str(val))
      hx.power_down()
      hx.power_up()
      time.sleep(0.05)
      
    print('Breath:'+str(bc*3))
    br=0
    bc=0


    print('Calculating HB and SPO2..')
    hrm = HeartRateMonitor()
    hrm.start_sensor()
    time.sleep(10)
    hb,spo2=hrm.stop_sensor()
    print('HB:' + str(hb))
    print('SPO2:'+str(spo2))

    heartrate=get_HB_data()
    print('HB:' +str(heartrate))
    print()
    time.sleep(0.5)

    temperature_celsius = sensor.get_temperature()
    temperature_fahrenheit = sensor.get_temperature(Unit.DEGREES_F)
    
    print("The temperature is %s Celsius" % temperature_celsius)
    print("The temperature is %s Fahrenheit" % temperature_fahrenheit)
    time.sleep(1)

    humidity,temparature=Adafruit_DHT.read(DHT_sensor,DHT_pin)
    print(f'temparature:{temparature}°C,humidity:{humidity}%')
    time.sleep(1)


    
