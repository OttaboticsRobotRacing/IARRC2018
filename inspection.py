'''
Drive 10m at 2m/s
'''

from communication import serial_communication
import time
import logging

runtime = 2

logging.basicConfig(level=logging.DEBUG)
print('Waiting 2 seconds')
time.sleep(2)
print('Starting')
start_time = time.time()

serial_communication.write_serial_message('s20')

while time.time() - start_time < runtime:
    serial_communication.write_serial_message('a70')
    #time.sleep(0.1)
    serial_communication.write_serial_message('a110')
    #time.sleep(0.1)

serial_communication.write_serial_message('s0')
serial_communication.write_serial_message('a90')
