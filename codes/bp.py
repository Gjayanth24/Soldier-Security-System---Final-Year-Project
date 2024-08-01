from gpiozero import MCP3208
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pres = MCP3208(channel=0, device=0)
breath = MCP3208(channel=2, device=0)


pval=(pres.value * 5) * 1000
bval=(breath.value * 5) * 1000

while(1):
    pval=(1-(pres.value))*200 
    
    print(pval)
   
    print()
    time.sleep(0.3)
