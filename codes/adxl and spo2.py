from heartrate_monitor import HeartRateMonitor
import time
import argparse
import smbus
import time
import RPi.GPIO as GPIO

bus = smbus.SMBus(1)
bus.write_byte_data(0x53, 0x2C, 0x0B)
value = bus.read_byte_data(0x53, 0x31)
value &= ~0x0F;
value |= 0x0B;  
value |= 0x08;
bus.write_byte_data(0x53, 0x31, value)
bus.write_byte_data(0x53, 0x2D, 0x08)

def getAxes():
    bytes = bus.read_i2c_block_data(0x53, 0x32, 6)
        
    x = bytes[0] | (bytes[1] << 8)
    if(x & (1 << 16 - 1)):
        x = x - (1<<16)

    y = bytes[2] | (bytes[3] << 8)
    if(y & (1 << 16 - 1)):
        y = y - (1<<16)

    z = bytes[4] | (bytes[5] << 8)
    if(z & (1 << 16 - 1)):
        z = z - (1<<16)

    x = x * 0.004 
    y = y * 0.004
    z = z * 0.004

    x = x * 9.80665
    y = y * 9.80665
    z = z * 9.80665

    x = round(x, 2)
    y = round(y, 2)
    z = round(z, 2)
    return x,y,z

def get_spo2_data():
    print('Calculating HB and SPO2..')
    hrm = HeartRateMonitor()
    hrm.start_sensor()
    time.sleep(10)
    hb,spo2=hrm.stop_sensor()
    #print('HB:' + str(hb))
    #print('SPO2:'+str(spo2))
    return hb,spo2

while True:
        fall = 0
        x,y,z=getAxes()
        hb,spo2=get_spo2_data()
        print('HB:' + str(hb))
        print('SPO2:'+str(spo2))
        if(x<-5 or x>5 or y<-5 or y>5):
            fall = 1
        print(fall)
        time.sleep(2)


    
        





