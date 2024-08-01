from heartrate_monitor import HeartRateMonitor
import time
import argparse


print('Calculating HB and SPO2..')
hrm = HeartRateMonitor()
hrm.start_sensor()
time.sleep(10)
hb,spo2=hrm.stop_sensor()
print('HB:' + str(hb))
print('SPO2:'+str(spo2))

