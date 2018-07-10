import serial
import time
import threading
import queue
from curtsies import Input # pip3 install curtsies
import logging

SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

def read_serial_thread(q):
    connected = False

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0)

        while not connected:
            connected = True

            while ser.isOpen():
                if (ser.inWaiting() > 0):
                    data_str = ser.read(ser.inWaiting()).decode('ascii')
                    print(data_str, end='')
                stay_alive = True
                if not q.empty():
                    stay_alive = q.get()
                if not stay_alive:
                    return
            print('end')
    except serial.serialutil.SerialException:
        print('Serial port not found')
        return

def read_serial():
    connected = False

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0)

        while not connected:
            connected = True

            while ser.isOpen():
                if (ser.inWaiting() > 0):
                    data_str = ser.read(ser.inWaiting()).decode('ascii')
                    #print(data_str)
                    return data_str.replace('\n', '').replace('\r','')
            #print('end')
    except serial.serialutil.SerialException:
        print('Serial port not found')
        return

def write_serial_message(message):
    message = message.encode('ascii')
    logging.debug('writing message: %s' % message)

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0)
    except serial.serialutil.SerialException:
        logging.debug('Serial port not found')
        return

    ser.close()
    ser.open()

    ser.write(message)

    ser.close()


def start_reader_thread():
    q = queue.Queue()

    reader = threading.Thread(target=read_serial_thread, args=(q,))
    reader.start()

    return reader, q

def stop_reader_thread(q):
    q.put(False)

def main():
    pass

if __name__ == '__main__':
    main()
