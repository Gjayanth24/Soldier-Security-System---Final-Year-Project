import time
import io
import picamera
import logging
import socketserver
import sys
from threading import Condition
from http import server
import RPi.GPIO as GPIO
from hx711 import HX711
from w1thermsensor import W1ThermSensor, Unit
import Adafruit_DHT
from max30102 import MAX30102
from heartrate_monitor import HeartRateMonitor
import Adafruit_MCP3008
import requests
import serial
import argparse
import os
import Adafruit_GPIO.SPI as SPI
import urllib.request		         
import webbrowser


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

DHT_PIN = 27
DHT_SENSOR = Adafruit_DHT.DHT11
sensor = W1ThermSensor()

heartbeat_pin = 26
GPIO.setup(heartbeat_pin, GPIO.IN)

CLK=11
MOSI=10
MISO=9
CS=8

mcp=Adafruit_MCP3008.MCP3008(clk=CLK,mosi=MOSI,miso=MISO,cs=CS)

referenceUnit = 1
hx = HX711(20, 21)
hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()
print("Tare done! Add weight now...")
bc=0

ser = serial.Serial ("/dev/ttyUSB0",timeout=1)
map_link=""

def temperature_sms():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    print("TEMPERATURE=",temperature)
    if temperature>35:
        print("sending SMS..")

        cmd='AT\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)
        cmd='AT+CMGF=1\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)                                             
        phno="6300984271"                          
        cmd='AT+CMGS="'+str(phno)+'"\r\n'
        ser.write(cmd.encode())
        rcv = ser.read(20)
        print(rcv)                        
        time.sleep(1)
        msg = "TEMPERATURE EXCEEDED.MAP LINK:"
        ser.write(msg.encode())
        cmd = map_link
        ser.write(cmd.encode())  # Message
        
        #ser.write(msg.encode())  # Message
        time.sleep(1)
        cmd = "\x1A"
        ser.write(cmd.encode()) # Enable to send SMS
        time.sleep(10)
        print('SMS Sent')
        time.sleep(1)

def spo2_sms():
    print('Calculating SPO2..')
    hrm = HeartRateMonitor()
    hrm.start_sensor()
    time.sleep(10)
    hb,spo2=hrm.stop_sensor()
    print("BLOOD OXYGEN=",spo2)
    if spo2<96:
        print("sending SMS..")

        cmd='AT\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)
        cmd='AT+CMGF=1\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)                                             
        phno="6300984271"                          
        cmd='AT+CMGS="'+str(phno)+'"\r\n'
        ser.write(cmd.encode())
        rcv = ser.read(20)
        print(rcv)                        
        time.sleep(1)
        msg = "BLOOD OXYGEN IS LOW.MAP LINK:"
        ser.write(msg.encode())
        cmd = map_link
        ser.write(cmd.encode())  # Message
        
        #ser.write(msg.encode())  # Message
        time.sleep(1)
        cmd = "\x1A"
        ser.write(cmd.encode()) # Enable to send SMS
        time.sleep(10)
        print('SMS Sent')
        time.sleep(1)

def heartbeat_sms():
    print('please wear HB sensor clip to your finger')
    cnt = 0
    tempv = time.time()
    while time.time() < (tempv + 7):
        if GPIO.input(heartbeat_pin) == GPIO.LOW:
            cnt += 1
            time.sleep(0.4)
    cnt = cnt * 7
    heartrate = cnt
    cnt = 0
    print("HEART RATE=",heartrate)
    if heartrate>85:
        print("sending SMS..")

        cmd='AT\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)
        cmd='AT+CMGF=1\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)                                             
        phno="6300984271"                          
        cmd='AT+CMGS="'+str(phno)+'"\r\n'
        ser.write(cmd.encode())
        rcv = ser.read(20)
        print(rcv)                        
        time.sleep(1)
        msg = "HIGH HEART RATE.MAP LINK:"
        ser.write(msg.encode())
        cmd = map_link
        ser.write(cmd.encode())  # Message
        
        #ser.write(msg.encode())  # Message
        time.sleep(1)
        cmd = "\x1A"
        ser.write(cmd.encode()) # Enable to send SMS
        time.sleep(10)
        print('SMS Sent')
        time.sleep(1)

def breath_sms():
    global bc# declare bc as global
    referenceUnit = 1
    hx = HX711(20, 21)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(referenceUnit)
    hx.reset()
    hx.tare()
    tp = 0

    while tp < 10:
        val = hx.get_weight(5) / 1000
        if val < 10:
            val = 0
        if val > 20:
            bc += 1
        time.sleep(1)
        tp += 1
        hx.power_down()
        hx.power_up()
        time.sleep(0.05)

    breath = bc * 3
    bc = 0  # reset bc for the next calculation

    print('Breath:', breath)

    if breath > 10:
        print("sending SMS..")
        print("sending SMS..")

        cmd='AT\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)
        cmd='AT+CMGF=1\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)                                             
        phno="6300984271"                          
        cmd='AT+CMGS="'+str(phno)+'"\r\n'
        ser.write(cmd.encode())
        rcv = ser.read(20)
        print(rcv)                        
        time.sleep(1)
        msg = "HIGH BREATH COUNT.MAP LINK:"
        ser.write(msg.encode())
        cmd = map_link
        ser.write(cmd.encode())  # Message
        
        #ser.write(msg.encode())  # Message
        time.sleep(1)
        cmd = "\x1A"
        ser.write(cmd.encode()) # Enable to send SMS
        time.sleep(10)
        print('SMS Sent')
        time.sleep(1)

def mq6_sms():
    value=mcp.read_adc(4)
    print("GAS CONTENT=",value)
    if value>150:
        print("sending SMS..")

        cmd='AT\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)
        cmd='AT+CMGF=1\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)                                             
        phno="6300984271"                          
        cmd='AT+CMGS="'+str(phno)+'"\r\n'
        ser.write(cmd.encode())
        rcv = ser.read(20)
        print(rcv)                        
        time.sleep(1)
        msg = "SOLDIER IS SUFFERING FROM HARMFUL GASES.MAP LINK:"
        ser.write(msg.encode())
        cmd = map_link
        ser.write(cmd.encode())  # Message
        
        #ser.write(msg.encode())  # Message
        time.sleep(1)
        cmd = "\x1A"
        ser.write(cmd.encode()) # Enable to send SMS
        time.sleep(10)
        print('SMS Sent')
        time.sleep(1)

def ds18b20_sms():
    temperature_celsius = sensor.get_temperature()
    temperature_fahrenheit = sensor.get_temperature(Unit.DEGREES_F)
    print("TEMPERATURE(C)=",temperature_celsius)
    print("--------------------")
    print("TEMPERATURE(F)=",temperature_fahrenheit)
    if temperature_celsius>45:
        print("sending SMS..")

        cmd='AT\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)
        cmd='AT+CMGF=1\r\n'
        ser.write(cmd.encode())
        time.sleep(2)
        rcv = ser.read(20)
        print(rcv)                                             
        phno="6300984271"                          
        cmd='AT+CMGS="'+str(phno)+'"\r\n'
        ser.write(cmd.encode())
        rcv = ser.read(20)
        print(rcv)
        msg = "BODY TEMPERATURE IS HIGH.MAP LINK:"
        ser.write(msg.encode())
        cmd = map_link
        ser.write(cmd.encode())  # Message
        
        #ser.write(msg.encode())  # Message
        time.sleep(1)
        cmd = "\x1A"
        ser.write(cmd.encode()) # Enable to send SMS
        time.sleep(10)
        print('SMS Sent')
        time.sleep(1)

PAGE = """\
<!DOCTYPE html>
<html>
<head>
<title>SOLDIER'S HEALTH MONITORING SYSTEM</title>
</head>
<style>
    .sensor-container {
        display: flex;
        justify-content: flex-start;
        gap: 25px;
    }

    .sensor-box {
        border: 2px solid #ccc;
        padding: 10px;
        height: 70px;
        width: 285px;
        background-color: blue;
        border-radius: 10px;
    }

    h4 { color: pink; }
</style>
<body style="background-color: white;">

<center>
    <h1>SOLDIER'S HEALTH MONITORING SYSTEM</h1>
    <img src="stream.mjpg" width="980" height="500">
    <div id="response_message"></div>
</center>
<div id="response_message"></div>
<div class="sensor-container">
    <div class="sensor-box">
        <h4><div id="spo2">SPO2: ??</div></h4>
    </div>
    <div class="sensor-box">
        <h4><div id="heartbeat">HEARTBEAT: ??</div></h4>
    </div>
    <div class="sensor-box">
        <h4><div id="bodytemperature">BODY TEMPERATURE: ??</div></h4>
    </div>
    <div class="sensor-box">
        <h4><div id="temperature">TEMPERATURE: ??</div></h4>
    </div>
    <div class="sensor-box">
        <h4><div id="humidity">HUMIDITY: ??</div></h4>
    </div>
    <div class="sensor-box">
        <h4><div id="breath">BREATH: ??</div></h4>
    </div>
    <div class="sensor-box">
        <h4><div id="mq6_value">MQ6_VALUE: ??</div></h4>
    </div>
</div>

<script>
    function updateGPUTemperature() {
        fetch('/get_temperature')
            .then(response => response.text())
            .then(temp => {
                document.getElementById("temperature").innerText = `Temperature: ${temp} C`;
            });
    }
    
    function updatespo2() {
        fetch('/get_spo2')
            .then(response => response.text())
            .then(spo2 => {
                document.getElementById("spo2").innerText = `spo2: ${spo2}`;
            });
    }

    function updateheartbeat() {
        fetch('/get_heartbeat')
            .then(response => response.text())
            .then(heartbeat => {
                document.getElementById("heartbeat").innerText = `heartbeat: ${heartbeat}`;
            });
    }

    function updatebodytemperature() {
        fetch('/get_temperature_celsius')
            .then(response => response.text())
            .then(bodyTemperature => {
                document.getElementById("bodytemperature").innerText = `Body Temperature: ${bodyTemperature} °C`;
            });
    }

    function updatehumidity() {
        fetch('/get_humidity')
            .then(response => response.text())
            .then(humidity => {
                document.getElementById("humidity").innerText = `Humidity: ${humidity} %`;
            });
    }

    function updatebreath() {
        fetch('/get_breath')
            .then(response => response.text())
            .then(breath => {
                document.getElementById("breath").innerText = `breath: ${breath}`;
            });
    }

    function updatemq6_value() {
        fetch('/get_mq6_value')
            .then(response => response.text())
            .then(mq6_value => {
                document.getElementById("mq6_value").innerText = `mq6_Value: ${mq6_value}`;
            });
    }
    setInterval(updateGPUTemperature, 10000);
    setInterval(updatespo2, 10000);
    setInterval(updateheartbeat, 10000);
    setInterval(updatebodytemperature, 10000);
    setInterval(updatehumidity, 10000);
    setInterval(updatebreath, 10000);
    setInterval(updatemq6_value, 10000);
</script>
</body>
</html>
"""



            

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.error(f"Error in video stream: {e}")

        elif self.path=='/get_temperature':
            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
            temperature = str(temperature)
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(temperature))
            self.end_headers()
            self.wfile.write(temperature.encode('utf-8'))
            temperature_sms()

        elif self.path == '/get_spo2':
            hrm = HeartRateMonitor()
            hrm.start_sensor()
            time.sleep(10)
            hb,spo2=hrm.stop_sensor()
            spo2 = str(spo2)  
            #spo2 = str("{:.2f}".format(spo2))
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(spo2))
            self.end_headers()
            self.wfile.write(spo2.encode('utf-8'))
            spo2_sms()
            
        elif self.path == '/get_heartbeat':
            cnt = 0
            tempv = time.time()
            while time.time() < (tempv + 7):
                if GPIO.input(heartbeat_pin) == GPIO.LOW:
                    cnt += 1
                    time.sleep(0.4)
            cnt = cnt * 7
            heartrate = cnt
            cnt = 0
            heartbeat = str(heartrate) 
            #heartbeat = str("{:.2f}".format(heartbeat))
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(heartbeat))
            self.end_headers()
            self.wfile.write(heartbeat.encode('utf-8'))
            heartbeat_sms()

        elif self.path == '/get_temperature_celsius':
            body_temperature = sensor.get_temperature()
            body_temperature = str("{:.2f}".format(body_temperature))
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(body_temperature))
            self.end_headers()
            self.wfile.write(body_temperature.encode('utf-8'))
            ds18b20_sms()

        elif self.path=='/get_humidity':
            humidity,temperature=Adafruit_DHT.read_retry(DHT_SENSOR,DHT_PIN)
            humidity=str(humidity)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(humidity))
            self.end_headers()
            self.wfile.write(humidity.encode('utf-8'))

        elif self.path == '/get_breath':
            global bc# declare bc as global
            referenceUnit = 1
            hx = HX711(20, 21)
            hx.set_reading_format("MSB", "MSB")
            hx.set_reference_unit(referenceUnit)
            hx.reset()
            hx.tare()
            tp = 0

            while tp < 10:
                val = hx.get_weight(5) / 1000
                if val < 10:
                    val = 0
                if val > 20:
                    bc += 1
                time.sleep(1)
                tp += 1
                hx.power_down()
                hx.power_up()
                time.sleep(0.05)

            breath = bc * 3
            bc = 0  # reset bc for the next calculation
            breath = str("{:.2f}".format(breath))  
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(breath))
            self.end_headers()
            self.wfile.write(breath.encode('utf-8'))
            breath_sms()

        elif self.path=='/get_mq6_value':
            value=mcp.read_adc(0)
            value=str(value)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Content-Length', len(value))
            self.end_headers()
            self.wfile.write(value.encode('utf-8'))
            mq6_sms()

    def do_POST(self):
       pass

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def GPS_Info():
    global NMEA_buff
    global lat_in_degrees
    global long_in_degrees
    nmea_time = []
    nmea_latitude = []
    nmea_longitude = []
    nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
    nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
    nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
    
    #print("NMEA Time: ", nmea_time,'\n')
    #print ("NMEA Latitude:", nmea_latitude,"NMEA Longitude:", nmea_longitude,'\n')
    try:
        lat = float(nmea_latitude)                  #convert string into float for calculation
        longi = float(nmea_longitude)               #convertr string into float for calculation
    except:
        lat=0
        longi=0
    lat_in_degrees = convert_to_degrees(lat)    #get latitude in degree decimal format
    long_in_degrees = convert_to_degrees(longi) #get longitude in degree decimal format
    

def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position

gpgga_info = "$GPGGA,"
ser = serial.Serial ("/dev/ttyUSB0",timeout=1)              #Open port with baud rate for raspberry pi zero- ttyAMA0   for raspberry pi3 ttyS0
GPGGA_buffer = 0
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0

kk=0

try:
    ii=0
    while(ii<10):
        print('Read GPS Data')
        received_data = (str)(ser.readline())                   #read NMEA string received
        GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string
        if(kk==0):
            lat_in_degrees=0
            lat_in_degrees=0
            map_link = 'http://maps.google.com/?q=' + str(lat_in_degrees) + ',' + str(long_in_degrees)    #create link to plot location on Google map

        if (GPGGA_data_available>0):
            kk=1
            GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string 
            NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
            GPS_Info()                                          #get time, latitude, longitude
        ii=ii+1
                        
    map_link = 'http://maps.google.com/?q=' + str(lat_in_degrees) + ',' + str(long_in_degrees)    #create link to plot location on Google map
    print("lat in degrees:", lat_in_degrees," long in degree: ", long_in_degrees, '\n')
    print()
    print(map_link)
    #ii=ii+1
    


    with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')

        try:
            address = ('',8010)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()

        finally:
            camera.stop_recording()
            GPIO.cleanup()
except Exception as e:
    logging.error(f"An error occurred: {e}")

            
            


        


        


        
   
        
    


        
        
