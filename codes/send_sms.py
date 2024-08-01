import os
import sys
import RPi.GPIO as GPIO

import time
import serial  # Import only the Serial class

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

ser = serial("/dev/ttyS0", baudrate=9600, timeout=1)  # Use Serial class directly


def send_sms():
    print("Sending SMS...")

    cmd = 'AT\r\n'
    ser.write(cmd.encode())
    time.sleep(2)
    rcv = ser.read(ser.inWaiting()).decode()
    print(rcv)

    cmd = 'AT+CMGF=1\r\n'
    ser.write(cmd.encode())
    time.sleep(2)
    rcv = ser.read(ser.inWaiting()).decode()
    print(rcv)

    phno = "9493258398"
    cmd = 'AT+CMGS="{}"\r\n'.format(phno)
    ser.write(cmd.encode())
    time.sleep(2)
    rcv = ser.read(ser.inWaiting()).decode()
    print(rcv)

    message = "test message"
    cmd = "{}\x1A".format(message)
    ser.write(cmd.encode())  # Message and Ctrl+Z to send
    time.sleep(10)

    rcv = ser.read(ser.inWaiting()).decode()
    print(rcv)

    print("SMS Sent")

try:
    send_sms()
except Exception as e:
    print("Error:", str(e))
finally:
    ser.close()
    GPIO.cleanup()
